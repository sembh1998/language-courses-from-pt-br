#let topic = sys.inputs.at("topic", default: "topics/a1/02-greetings")
#let data = yaml(topic + "/exercises.yaml")

#set document(title: "German Exercises")
#set page(paper: "a4", margin: (x: 2cm, y: 2cm))
#set text(size: 11pt, lang: "en")
#set heading(numbering: "1.")
#set par(leading: 0.65em)

#show heading: it => [
  #v(0.8em)
  #it
  #v(0.4em)
]

= Exercises

Topic: #data.topic\
Level: #data.level

#for exercise in data.exercises [
  == #exercise.type

  *Instruction:* #exercise.instruction

  #v(0.4em)

  #for item in exercise.items [
    - #item.question
    #if "options" in item [
      #for choice in item.options [
        - #choice
      ]
    ]
    #v(0.9cm)
  ]
]
