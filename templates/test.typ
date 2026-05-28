#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let test = yaml(topic + "/test.yaml")

#show: doc => workbook(doc, title: test.topic + " Test", kind: "Test", accent: blue, margin: (x: 1.45cm, y: 1.5cm), body-size: 10.2pt)

#let test-question(question, number) = block(
  width: 100%,
  fill: surface,
  stroke: 0.65pt + sand,
  radius: 9pt,
  inset: 10pt,
  breakable: false,
)[
  #grid(columns: (auto, 1fr), gutter: 7pt, align: horizon)[
    #number-badge(str(number), fill: blue)
    #text(weight: "bold")[#question.question]
  ]

  #if "options" in question [
    #v(0.3em)
    #grid(
      columns: (1fr, 1fr, 1fr),
      gutter: 6pt,
      ..question.options.map(option => checkbox(option))
    )
  ] else [
    #answer-line()
  ]
]

#hero(test.topic + " Test", kind: "Test", level: test.level, accent: blue)

#v(0.6em)
#block(width: 100%, fill: blue-soft, stroke: 0.6pt + blue, radius: 9pt, inset: 10pt)[
  #text(font: ui-font, size: 8.5pt, weight: "bold", fill: muted)[Name]
  #v(0.15em)
  #line(length: 100%, stroke: 0.75pt + blue)
  #v(0.35em)
  #text(font: ui-font, size: 8.5pt, weight: "bold", fill: muted)[Date]
  #v(0.15em)
  #line(length: 100%, stroke: 0.75pt + blue)
]

#v(0.75em)

#for (index, question) in test.questions.enumerate() [
  #test-question(question, index + 1)
  #v(0.5em)
]
