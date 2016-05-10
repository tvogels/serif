#!/usr/bin/env node

Cheerio   = require('cheerio');
Citeproc  = require('citeproc');
yaml      = require('yamljs');
assert    = require('assert');
fs        = require('fs');

assert(process.argv.length > 2, "Please specify a file to link.");
var file = process.argv[2];


$ = Cheerio.load(fs.readFileSync(file, 'utf-8'));

var bibfile = yaml.parse(fs.readFileSync("../testbib.yaml", "utf-8"));
var locale = "en-US";
var style = "chicago-author-date";
countingConfig = {
  children: {
    'root': ['.section1'],
    '.section1': ['.section2','figure','theorem','table','.eqn-display[id]','listing'],
    '.section2': ['.section3'],
    '.section3': ['.section4']
  }
};

function setCounters(element, selectorList, base) {
  selectorList.forEach((selector) => {
    var findfnc = element.find || element;
    findfnc = findfnc.bind(element);
    findfnc(selector+':not(.no-number)').each((i, match) => {
      var count = base + (i+1);
      $(match).attr('data-counter', count);
      if (countingConfig.children[selector]) {
        setCounters($(match), countingConfig.children[selector], count+".");
      }
    });
  });
}

setCounters($, countingConfig.children.root, "");


// Process TOC
$('.toc a').each((i, link) => {
  var $this = $(link);
  var $target = $($this.attr('href'));
  if($target.hasClass('no-toc')) {
    $this.parent().remove();
  }
});

var bibIds = Object.keys(bibfile);
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
    if (bibIds.indexOf(targetId) >= 0) {
      $this.addClass('serif-citation-t');
      $this.attr('data-bib-id', targetId);
      $this.attr('href', `#bib:${targetId}`)
    } else {
      // not ofund
      $this.addClass('serif-reference-not-found');
    }
  }
});

// Do bibliography
// console.log(bibfile.doe99);
new Citeproc(bibfile,
             `../styles/${style}.csl`,
             `../locales/locales-${locale}.xml`,
function (citeproc) {

  var cite = (items) => {
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
      cites = [{id: $this.attr('data-bib-id'), 'author-only': true}];
      var part1 = cite(cites)[0][1];
      cites = [{id: $this.attr('data-bib-id'), 'suppress-author': true}];
      var part2 = cite(cites)[0][1];
      $this.html(part1 + ' ' + part2)
    } else {
      var data = JSON.parse($this.attr('data-items'));
      var res = cite(data);
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

  console.log($.html());
});





