#let ink = rgb("#1f2a44")
#let muted = rgb("#667085")
#let paper = rgb("#fbf3e4")
#let surface = rgb("#fffaf1")
#let sand = rgb("#dfcfb0")
#let amber = rgb("#e6a52e")
#let amber-soft = rgb("#fff0bf")
#let teal = rgb("#2f9c95")
#let teal-soft = rgb("#dff4ee")
#let blue = rgb("#315f9c")
#let blue-soft = rgb("#e6eef9")
#let rose = rgb("#bb4f5f")

#let ui-font = "Lato"
#let body-font = ("Noto Serif", "Libertinus Serif")

#let icon(label, fill: teal) = rect(
  width: 23pt,
  height: 23pt,
  radius: 11.5pt,
  fill: fill,
  stroke: 0pt,
)[
  #align(center + horizon)[
    #text(font: ui-font, size: 7.4pt, weight: "bold", fill: surface)[#label]
  ]
]

#let pill(body, fill: amber-soft, stroke: amber, text-fill: ink) = block(
  fill: fill,
  stroke: 0.45pt + stroke,
  radius: 99pt,
  inset: (x: 6pt, y: 2pt),
)[
  #text(font: ui-font, size: 7.2pt, weight: "bold", fill: text-fill)[#body]
]

#let number-badge(number, fill: blue) = rect(
  width: 16pt,
  height: 16pt,
  radius: 8pt,
  fill: fill,
  stroke: 0pt,
)[
  #align(center + horizon)[
    #text(font: ui-font, size: 7pt, weight: "bold", fill: surface)[#number]
  ]
]

#let section-heading(body, accent: teal) = [
  #v(0.55em)
  #grid(columns: (auto, 1fr), gutter: 6pt, align: horizon)[
    #rect(width: 4.5pt, height: 14pt, radius: 2.25pt, fill: accent)
    #text(font: ui-font, size: 12.2pt, weight: "black", fill: ink)[#body]
  ]
  #v(0.1em)
]

#let hero(title, kind: "Lesson", level: none, accent: teal) = block(
  width: 100%,
  fill: surface,
  stroke: 0.65pt + sand,
  radius: 8pt,
  inset: 9pt,
)[
  #grid(columns: (auto, 1fr), gutter: 8pt, align: horizon)[
    #icon(kind.first(), fill: accent)
    #block(width: 100%)[
      #text(font: ui-font, size: 7.5pt, weight: "bold", fill: muted)[CADERNO DE ALEMÃO]
      #v(0.08em)
      #text(font: ui-font, size: 17.2pt, weight: "black", fill: ink)[#title]
      #v(0.16em)
      #grid(columns: (auto, auto, 1fr), gutter: 4pt)[
        #pill(kind, fill: teal-soft, stroke: teal)
        #if level != none [#pill("Nível " + level, fill: amber-soft, stroke: amber)]
      ]
    ]
  ]
]

#let answer-line(width: 100%) = [
  #v(0.12em)
  #line(length: width, stroke: 0.65pt + blue)
]

#let checkbox(label) = [
  #rect(width: 6pt, height: 6pt, radius: 1.2pt, stroke: 0.75pt + teal)
  #h(3pt)
  #label
]

#let workbook(body, title: "Caderno de alemão", kind: "Lição", accent: teal, margin: (x: 1.65cm, y: 1.7cm), body-size: 10.5pt) = {
  set document(title: title)
  set page(
    paper: "a4",
    margin: margin,
    fill: paper,
    header: align(right)[
      #text(font: ui-font, size: 7pt, weight: "bold", fill: muted)[Alemão para PT-BR]
    ],
    footer: [
      #line(length: 100%, stroke: 0.4pt + sand)
      #v(0.08em)
      #align(right)[#text(font: ui-font, size: 7pt, fill: muted)[página #context counter(page).display("1")]]
    ],
  )
  set text(font: body-font, size: body-size, lang: "pt", fill: ink)
  set par(leading: 0.56em, justify: false)
  set heading(numbering: none)
  set table(stroke: 0.5pt + sand, inset: 4pt)
  set list(marker: ([#text(fill: teal)[•]],))

  show heading: it => {
    if it.level == 1 {
      hero(it.body, kind: kind, accent: accent)
      v(0.45em)
    } else if it.level == 2 {
      section-heading(it.body, accent: accent)
    } else {
      v(0.45em)
      text(font: ui-font, size: 10.3pt, weight: "bold", fill: ink)[#it.body]
      v(0.08em)
    }
  }

  show strong: set text(fill: blue, weight: "bold")
  show table.cell.where(y: 0): set table.cell(fill: amber-soft)
  show table.cell.where(y: 0): set text(font: ui-font, weight: "bold", fill: ink)

  body
}
