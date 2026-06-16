#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let course-label = sys.inputs.at("course-label", default: "Alemão para PT-BR")
#let target-language-pt = sys.inputs.at("target-language-pt", default: "alemão")
#let lesson-number = sys.inputs.at("lesson-number", default: none)
#let data = yaml(topic + "/flashcards.yaml")
#let topic-title = data.at("topic", default: "Tópico")
#let topic-level = data.at("level", default: "A1")

#show: doc => workbook(doc, title: "Cartões de estudo de " + target-language-pt, kind: "Cartões", accent: rose, course-label: course-label, lesson-number: lesson-number, margin: (x: 1.05cm, y: 1.05cm), body-size: 9.2pt)

#let card-number(n) = pill("#" + str(n), fill: blue-soft, stroke: blue, text-fill: blue)

#let flashcard(card, number) = block(
  width: 100%,
  height: 3.55cm,
  fill: surface,
  stroke: (top: 1.4pt + rose, rest: 0.55pt + sand),
  radius: 7pt,
  inset: 0pt,
  breakable: false,
)[
  #block(inset: (x: 6pt, y: 5pt))[#grid(columns: (1fr, auto), gutter: 4pt, align: horizon)[
    #text(font: ui-font, size: 9.6pt, weight: "black", fill: ink)[#card.front]
    #card-number(number)
  ]]
  #block(inset: (x: 6pt, y: 1pt))[#text(size: 8.2pt, fill: ink)[#card.back]]
  #block(inset: (x: 6pt, y: 2pt))[#line(length: 100%, stroke: 0.35pt + sand)]
  #block(inset: (x: 6pt, y: 1pt))[#text(size: 7.4pt)[#card.example]\
  #text(size: 7pt, style: "italic", fill: muted)[#card.example_translation]]
]

#hero("Cartões de estudo", kind: "Cartões", level: topic-level, accent: rose, course-label: course-label, lesson-number: lesson-number)

#v(0.25em)
#pill(topic-title, fill: amber-soft, stroke: amber)
#v(0.35em)

#grid(
  columns: (1fr, 1fr),
  gutter: 8pt,
  ..data.cards.enumerate().map(((index, card)) => flashcard(card, index + 1))
)
