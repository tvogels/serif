Cheerio   = require('cheerio');
Citeproc  = require('citeproc');
yaml      = require('yamljs');
assert    = require('assert');
fs        = require('fs');
CSL       = require('citeproc').CSL;


CONFIG = [[CONFIG_PLACEHOLDER]];
// process.chdir("[[WORKING_DIRECTORY]]");

/**
 * Helper function to take elements from config if they exist
 */
function conf() {
  current = CONFIG
  for (var i = 0; i < arguments.length; i++) {
    if (current.hasOwnProperty(arguments[i]))
      current = current[arguments[i]];
    else
      return null;
  }
  return current;
}

/**
 * Load file helper
 */
function load(filename) {
  try {
    return fs.readFileSync(filename, 'utf-8');
  } catch (e) {
    throw `Failed to load file '${filename}', error: ${JSON.stringify(e)}`;
  }
}

/**
 * Main function, takes HTML and applies all the edits to it.
 */
function link(html) {
  const $ = Cheerio.load(html);

  counting($);

  toc($);
  // Load the bibliography if desired
  var bib = [];
  if (conf('bibliography','enabled'))
    bib = loadBibliography();

  references($, bib);

  if (conf('bibliography','enabled'))
    citationsAndBibliography($, bib);

  return $.html();
}

/**
 * Set the data-counter element on everything that should be counted
 */
function counting($) {
  function setCounters(element, selectorList, base) {
    selectorList.forEach((selector) => {
      var findfnc = element.find || element;
      findfnc = findfnc.bind(element);
      findfnc(selector+':not(.no-number)').each((i, match) => {
        var count = base + (i+1);
        $(match).attr('data-counter', count);
        $(match).find('>h1:first-child,>h2:first-child,>h3:first-child,>h4:first-child,>h5:first-child,>h6:first-child,>caption,>figcaption').attr('data-counter', count);
        if (conf('counting', selector)) {
          setCounters($(match), conf('counting', selector), count+".");
        }
      });
    });
  }
  setCounters($, conf('counting', 'root'), "");
}

/**
 * Clean .no-toc references from the Table of Contents
 */
function toc($) {
  $('.toc a').each((i, link) => {
    var $this = $(link);
    var $target = $($this.attr('href'));
    if($target.hasClass('no-toc')) {
      $this.parent().remove();
    }
  });
}

/**
 * Load the bibliography
 */
function loadBibliography() {
  var path = conf('bibliography','library');
  try {
    var res = yaml.load(path);
    if (typeof res === 'object' && res !== null) {
      return res;
    } else {
      return {};
    }
  } catch (e) {
    throw `Failed to load bibliography file at '${path}', error: ${JSON.stringify(e)}`;
  }
}


/**
 * Link cross-references, and set target counters
 */
function references($, bib) {
  // Process links & prepare simple citations (not block)
  $("[href*='#']").each((i, reference) => {
    $this = $(reference);
    var targetId = $this.attr('href').substr(1);
    var $target = $("[id='"+targetId+"']");
    if ($target.length > 0) {
      $this.attr('data-target-counter', $target.attr('data-counter'));
    } else {
      targetId = targetId.replace(/^bib:/,'');
      // Could be bibiliography ...
      if (bib[targetId] !== undefined) {
        $this.addClass('serif-citation-t');
        $this.attr('data-bib-id', targetId);
        $this.attr('href', `#bib:${targetId}`)
      } else {
        // not found
        $this.text(`@${targetId}`)
        $this.addClass('serif-reference-not-found');
      }
    }
  });
}

/**
 * Get a configured citeproc instance
 */
function getCiteproc(bib) {
  const style  = load(`[[SERIF_ROOT]]/styles/${conf('bibliography', 'style')}.csl`);
  const locale = load(`[[SERIF_ROOT]]/locales/locales-${conf('locale').replace('_','-')}.xml`);
  sys = {
    retrieveLocale: function (language) {
        return locale;
    },
    retrieveItem: function (id) {
      return bib[id];
    }
  };
  return new CSL.Engine(sys, style);
}

/**
 * Do all citations, blocks and simple ones, and create the bibliography
 */
function citationsAndBibliography($, bib) {

  const citeproc = getCiteproc(bib);

  const cite = (items) => {
    return citeproc.appendCitationCluster({
            citationItems: items,
            properties: {noteIndex: 0}
    });
  };

  $(".serif-citation-block, .serif-citation-t").each((i, reference) => {
    $this = $(reference);
    var cites = [];
    if ($this.hasClass('serif-citation-t')) {
      // Vogels (2006), single
      const cite_id = $this.attr('data-bib-id');
      // Check if there is a bibentry
      if (bib[cite_id] === undefined) {
        $this.text(`[@${cite_id}]`);
        $this.addClass('serif-reference-not-found');
        return;
      }
      try {
        cites = [{id: cite_id, 'author-only': true}];
        const part1 = cite(cites)[0][1];
        cites = [{id: cite_id, 'suppress-author': true}];
        const part2 = cite(cites)[0][1];
      } catch (e) {
        throw `Citing ${cite_id} failed (${JSON.stringify(e)}).`;
      }
      $this.html(part1 + ' ' + part2)
    } else {
      // Multiple, put in a block
      var data = JSON.parse($this.attr('data-items'));

      // Check the data
      for (var i = data.length - 1; i >= 0; i--) {
        var d = data[i];
        if (bib[d.id] === undefined) {
          $this.text(`[@${d.id}]`);
          $this.addClass('serif-reference-not-found');
          return;
        }
      };
      try {
        var res = cite(data);
      } catch (e) {
        throw `Citing ${JSON.stringify(data.map((d) => d.id))} failed.`;
      }
      $this.html(res[0][1]);
      if (data.length == 1)
        $this.attr('href', `#bib:${data[0].id}`)
      else
        $this.attr('href', `#serif-bibliography`)
    }
  });
  $bib = $('.serif-bibliography');
  var bibres = citeproc.makeBibliography();
  $bib.html(bibres[1].join(''))
  $bib.attr('data-maxoffset', bibres[0].maxoffset);
  $bib.attr('data-hangingindent', bibres[0].hangingindent);
  $bib.attr('data-entryspacing', bibres[0].entryspacing);
  $bib.attr('data-linespacing', bibres[0].linespacing);
  $bib.attr('data-second-field-align', bibres[0]['second-field-align']);

  $bib.find('[data-item-id]').each((i, elem) => {
    $(elem).attr('id', `bib:${$(elem).attr('data-item-id')}`);
  });

}



