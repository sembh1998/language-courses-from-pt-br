#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let data = yaml(topic + "/exercises.yaml")

#show: doc => workbook(doc, title: "Exercícios de alemão", kind: "Prática", accent: teal, margin: (x: 1.05cm, y: 1.05cm), body-size: 9.1pt)

#let exercise-title(kind) = if kind == "multiple_choice" {
  "Múltipla escolha"
} else if kind == "fill_blank" {
  "Complete as lacunas"
} else if kind == "short_answer" {
  "Resposta curta"
} else if kind == "translation" {
  "Tradução"
} else if kind == "matching" {
  "Associação"
} else if kind == "ordering" {
  "Ordenação"
} else if kind == "transformation" {
  "Transformação"
} else if kind == "correction" {
  "Correção"
} else if kind == "classification" {
  "Classificação"
} else if kind == "production" {
  "Produção"
} else if kind == "contrast" {
  "Contraste"
} else {
  kind.replace("_", " ")
}

#let option-chip(choice) = block(
  width: 100%,
  fill: surface,
  stroke: 0.45pt + teal,
  radius: 4pt,
  inset: (x: 5pt, y: 3pt),
)[
  #text(font: ui-font, size: 8.5pt, weight: "bold", fill: teal)[□]
  #h(3pt)
  #text(size: 8.6pt)[#choice]
]

#let exercise-item(item, number) = block(
  width: 100%,
  fill: paper,
  stroke: 0.45pt + sand,
  radius: 5pt,
  inset: 5pt,
  breakable: false,
)[
  #grid(columns: (auto, 1fr), gutter: 5pt, align: horizon)[
    #pill(str(number), fill: blue-soft, stroke: blue, text-fill: blue)
    #text(weight: "bold")[#item.question]
  ]
  #if "options" in item [
    #v(0.25em)
    #grid(
      columns: (1fr, 1fr, 1fr),
      gutter: 5pt,
      ..item.options.map(choice => option-chip(choice))
    )
  ] else [
    #answer-line()
  ]
]

#let exercise-card(exercise, number) = block(
  width: 100%,
  fill: surface,
  stroke: 0.6pt + sand,
  radius: 7pt,
  inset: 7pt,
  breakable: true,
)[
  #let exercise-header = block(width: 100%, fill: teal-soft, stroke: 0.45pt + teal, radius: 5pt, inset: 6pt)[
    #grid(columns: (auto, 1fr), gutter: 6pt, align: horizon)[
      #number-badge(str(number), fill: teal)
      #block(width: 100%)[
        #text(font: ui-font, size: 10.6pt, weight: "black", fill: ink)[#exercise-title(exercise.type)]
        #v(0.06em)
        #text(font: ui-font, size: 7.8pt, weight: "bold", fill: muted)[#exercise.instruction]
      ]
    ]
  ]

  #if exercise.items.len() > 0 [
    #block(breakable: false)[
      #exercise-header
      #v(0.35em)
      #exercise-item(exercise.items.at(0), 1)
    ]
    #v(0.25em)
    #for (index, item) in exercise.items.enumerate() [
      #if index > 0 [
        #exercise-item(item, index + 1)
        #v(0.25em)
      ]
    ]
  ] else [
    #exercise-header
  ]
]

#hero("Exercícios", kind: "Prática", level: data.level, accent: teal)

#v(0.25em)
#pill(data.topic, fill: amber-soft, stroke: amber)
#v(0.45em)

#for (index, exercise) in data.exercises.enumerate() [
  #exercise-card(exercise, index + 1)
  #v(0.4em)
]
