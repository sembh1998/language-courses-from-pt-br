#let topic = sys.inputs.at("topic", default: "topics/a1/02-greetings")
#let lesson = read(topic + "/lesson.md")

#set document(title: "German Lesson")
#set page(paper: "a4", margin: (x: 2cm, y: 2cm))
#set text(size: 11pt, lang: "en")
#set heading(numbering: "1.")
#set par(leading: 0.65em)

#show heading: it => [
  #v(0.8em)
  #it
  #v(0.4em)
]

#lesson
