#let topic = sys.inputs.at("topic", default: "topics/a1/02-greetings")
#let data = yaml(topic + "/flashcards.yaml")

#set document(title: "German Flashcards")
#set page(paper: "a4", margin: (x: 2cm, y: 2cm))
#set text(size: 11pt, lang: "en")
#set heading(numbering: "1.")
#set par(leading: 0.65em)

#show heading: it => [
  #v(0.8em)
  #it
  #v(0.4em)
]

= Flashcards

Topic: #data.topic\
Level: #data.level

#v(1em)

#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,
  ..data.cards.map(card => box(
    width: 100%,
    height: 4.5cm,
    stroke: 0.6pt,
    inset: 12pt,
    [
      #strong(card.front)\
      #card.back\
      #v(0.4em)
      #card.example\
      #emph(card.example_translation)
    ],
  ))
)
