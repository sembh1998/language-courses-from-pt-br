#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let test = yaml(topic + "/test.yaml")

#show: doc => workbook(doc, title: test.topic + " - Teste", kind: "Teste", accent: blue, margin: (x: 1.05cm, y: 1.05cm), body-size: 9.1pt)

#let test-question(question, number) = block(
  width: 100%,
  fill: surface,
  stroke: 0.55pt + sand,
  radius: 6pt,
  inset: 6pt,
  breakable: false,
)[
  #grid(columns: (auto, 1fr), gutter: 5pt, align: horizon)[
    #number-badge(str(number), fill: blue)
    #text(weight: "bold")[#question.question]
  ]

  #if "options" in question [
    #v(0.2em)
    #grid(
      columns: (1fr, 1fr, 1fr),
      gutter: 5pt,
      ..question.options.map(option => checkbox(option))
    )
  ] else [
    #answer-line()
  ]
]

#hero(test.topic + " - Teste", kind: "Teste", level: test.level, accent: blue)

#v(0.35em)
#block(width: 100%, fill: blue-soft, stroke: 0.55pt + blue, radius: 6pt, inset: 6pt)[
  #grid(columns: (1fr, 1fr), gutter: 12pt)[
    #block(width: 100%)[
      #text(font: ui-font, size: 7.6pt, weight: "bold", fill: muted)[Nome]
      #v(0.08em)
      #line(length: 100%, stroke: 0.65pt + blue)
    ]
    #block(width: 100%)[
      #text(font: ui-font, size: 7.6pt, weight: "bold", fill: muted)[Data]
      #v(0.08em)
      #line(length: 100%, stroke: 0.65pt + blue)
    ]
  ]
]

#v(0.45em)

#for (index, question) in test.questions.enumerate() [
  #test-question(question, index + 1)
  #v(0.28em)
]
