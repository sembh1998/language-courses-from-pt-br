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
  width: 30pt,
  height: 30pt,
  radius: 15pt,
  fill: fill,
  stroke: 0pt,
)[
  #align(center + horizon)[
    #text(font: ui-font, size: 9pt, weight: "bold", fill: surface)[#label]
  ]
]

#let pill(body, fill: amber-soft, stroke: amber, text-fill: ink) = block(
  fill: fill,
  stroke: 0.45pt + stroke,
  radius: 99pt,
  inset: (x: 8pt, y: 3pt),
)[
  #text(font: ui-font, size: 8pt, weight: "bold", fill: text-fill)[#body]
]

#let number-badge(number, fill: blue) = rect(
  width: 19pt,
  height: 19pt,
  radius: 9.5pt,
  fill: fill,
  stroke: 0pt,
)[
  #align(center + horizon)[
    #text(font: ui-font, size: 8pt, weight: "bold", fill: surface)[#number]
  ]
]

#let section-heading(body, accent: teal) = [
  #v(0.9em)
  #grid(columns: (auto, 1fr), gutter: 8pt, align: horizon)[
    #rect(width: 6pt, height: 18pt, radius: 3pt, fill: accent)
    #text(font: ui-font, size: 14pt, weight: "black", fill: ink)[#body]
  ]
  #v(0.2em)
]

#let hero(title, kind: "Lesson", level: none, accent: teal) = block(
  width: 100%,
  fill: surface,
  stroke: 0.8pt + sand,
  radius: 12pt,
  inset: 14pt,
)[
  #grid(columns: (auto, 1fr), gutter: 12pt, align: horizon)[
    #icon(kind.first(), fill: accent)
    #block(width: 100%)[
      #text(font: ui-font, size: 8.5pt, weight: "bold", fill: muted)[DEUTSCH WORKBOOK]
      #v(0.2em)
      #text(font: ui-font, size: 21pt, weight: "black", fill: ink)[#title]
      #v(0.35em)
      #grid(columns: (auto, auto, 1fr), gutter: 6pt)[
        #pill(kind, fill: teal-soft, stroke: teal)
        #if level != none [#pill("Level " + level, fill: amber-soft, stroke: amber)]
      ]
    ]
  ]
]

#let answer-line(width: 100%) = [
  #v(0.25em)
  #line(length: width, stroke: 0.75pt + blue)
]

#let checkbox(label) = [
  #rect(width: 7pt, height: 7pt, radius: 1.5pt, stroke: 0.8pt + teal)
  #h(3pt)
  #label
]

#let workbook(body, title: "German Workbook", kind: "Lesson", accent: teal, margin: (x: 1.65cm, y: 1.7cm), body-size: 10.5pt) = {
  set document(title: title)
  set page(
    paper: "a4",
    margin: margin,
    fill: paper,
    header: align(right)[
      #text(font: ui-font, size: 8pt, weight: "bold", fill: muted)[Alemão para PT-BR]
    ],
    footer: [
      #line(length: 100%, stroke: 0.45pt + sand)
      #v(0.2em)
      #align(right)[#text(font: ui-font, size: 8pt, fill: muted)[página #context counter(page).display("1")]]
    ],
  )
  set text(font: body-font, size: body-size, lang: "pt", fill: ink)
  set par(leading: 0.68em, justify: false)
  set heading(numbering: none)
  set table(stroke: 0.55pt + sand, inset: 6pt)
  set list(marker: ([#text(fill: teal)[•]],))

  show heading: it => {
    if it.level == 1 {
      hero(it.body, kind: kind, accent: accent)
      v(0.8em)
    } else if it.level == 2 {
      section-heading(it.body, accent: accent)
    } else {
      v(0.7em)
      text(font: ui-font, size: 11.5pt, weight: "bold", fill: ink)[#it.body]
      v(0.15em)
    }
  }

  show strong: set text(fill: blue, weight: "bold")
  show table.cell.where(y: 0): set table.cell(fill: amber-soft)
  show table.cell.where(y: 0): set text(font: ui-font, weight: "bold", fill: ink)

  body
}
