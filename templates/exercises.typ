#import "theme.typ": *

#let topic = sys.inputs.at("topic", default: "topics/a1/001-alfabeto-alemao-e-sons-basicos")
#let data = yaml(topic + "/exercises.yaml")

#show: doc => workbook(doc, title: "German Exercises", kind: "Practice", accent: teal, margin: (x: 1.45cm, y: 1.5cm), body-size: 10.2pt)

#let exercise-title(kind) = if kind == "multiple_choice" {
  "Múltipla escolha"
} else if kind == "fill_blank" {
  "Complete as lacunas"
} else {
  kind.replace("_", " ")
}

#let option-chip(choice) = block(
  width: 100%,
  fill: surface,
  stroke: 0.45pt + teal,
  radius: 6pt,
  inset: (x: 7pt, y: 5pt),
)[
  #text(font: ui-font, size: 10pt, weight: "bold", fill: teal)[□]
  #h(4pt)
  #text(size: 9.5pt)[#choice]
]

#let exercise-item(item, number) = block(
  width: 100%,
  fill: paper,
  stroke: 0.45pt + sand,
  radius: 8pt,
  inset: 8pt,
  breakable: false,
)[
  #grid(columns: (auto, 1fr), gutter: 7pt, align: horizon)[
    #pill(str(number), fill: blue-soft, stroke: blue, text-fill: blue)
    #text(weight: "bold")[#item.question]
  ]
  #if "options" in item [
    #v(0.45em)
    #grid(
      columns: (1fr, 1fr, 1fr),
      gutter: 7pt,
      ..item.options.map(choice => option-chip(choice))
    )
  ] else [
    #answer-line()
  ]
]

#let exercise-card(exercise, number) = block(
  width: 100%,
  fill: surface,
  stroke: 0.75pt + sand,
  radius: 10pt,
  inset: 11pt,
  breakable: false,
)[
  #block(width: 100%, fill: teal-soft, stroke: 0.45pt + teal, radius: 8pt, inset: 8pt)[
    #grid(columns: (auto, 1fr), gutter: 8pt, align: horizon)[
      #number-badge(str(number), fill: teal)
      #block(width: 100%)[
        #text(font: ui-font, size: 12.5pt, weight: "black", fill: ink)[#exercise-title(exercise.type)]
        #v(0.15em)
        #text(font: ui-font, size: 8.8pt, weight: "bold", fill: muted)[#exercise.instruction]
      ]
    ]
  ]
  #v(0.6em)
  #for (index, item) in exercise.items.enumerate() [
    #exercise-item(item, index + 1)
    #v(0.45em)
  ]
]

#hero("Exercises", kind: "Practice", level: data.level, accent: teal)

#v(0.5em)
#pill(data.topic, fill: amber-soft, stroke: amber)
#v(0.8em)

#for (index, exercise) in data.exercises.enumerate() [
  #exercise-card(exercise, index + 1)
  #v(0.75em)
]
