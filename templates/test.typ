#let topic = sys.inputs.at("topic", default: "topics/a1/02-greetings")
#let test = yaml(topic + "/test.yaml")

#set document(title: test.topic + " Test")
#set page(paper: "a4", margin: (x: 2cm, y: 2cm))
#set text(size: 11pt, lang: "en")
#set heading(numbering: "1.")
#set par(leading: 0.65em)

#show heading: it => [
  #v(0.8em)
  #it
  #v(0.4em)
]

= #test.topic Test

Level: #test.level

Name: #line(length: 7cm) Date: #line(length: 4cm)

#v(1em)

#for question in test.questions [
  - #question.question

  #if "options" in question [
    #for option in question.options [
      - #option
    ]
  ]

  #v(1.2cm)
]
