#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let data = yaml(topic + "/flashcards.yaml")

#show: doc => workbook(doc, title: "German Flashcards", kind: "Cards", accent: rose, margin: (x: 1.35cm, y: 1.45cm), body-size: 10pt)

#let card-number(n) = pill("#" + str(n), fill: blue-soft, stroke: blue, text-fill: blue)

#let flashcard(card, number) = block(
  width: 100%,
  height: 5.45cm,
  fill: surface,
  stroke: (top: 2pt + rose, rest: 0.7pt + sand),
  radius: 10pt,
  inset: 0pt,
  breakable: false,
)[
  #block(inset: (x: 9pt, y: 8pt))[#grid(columns: (1fr, auto), gutter: 6pt, align: horizon)[
    #text(font: ui-font, size: 12.5pt, weight: "black", fill: ink)[#card.front]
    #card-number(number)
  ]]
  #block(inset: (x: 9pt, y: 3pt))[#text(size: 10.3pt, fill: ink)[#card.back]]
  #block(inset: (x: 9pt, y: 4pt))[#line(length: 100%, stroke: 0.45pt + sand)]
  #block(inset: (x: 9pt, y: 3pt))[#text(size: 9.3pt)[#card.example]\
  #text(size: 8.8pt, style: "italic", fill: muted)[#card.example_translation]]
]

#hero("Flashcards", kind: "Cards", level: data.level, accent: rose)

#v(0.5em)
#pill(data.topic, fill: amber-soft, stroke: amber)
#v(0.7em)

#grid(
  columns: (1fr, 1fr),
  gutter: 12pt,
  ..data.cards.enumerate().map(((index, card)) => flashcard(card, index + 1))
)
