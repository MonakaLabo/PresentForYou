let data=[]
let quiz=[]
let index=0
let correct=0
let startTime=0

function loadTable(name){

return fetch("../tables/"+name)
.then(r=>r.text())
.then(text=>{

return text.split("\n")
.filter(l=>l.trim()!="")
.map(l=>l.split("\t"))

})

}

function start(){

let table=document.getElementById("tableSelect").value
let count=parseInt(document.getElementById("count").value)
let order=document.getElementById("order").value
let direction=document.getElementById("direction").value

loadTable(table).then(d=>{

data=d

if(order==="random")
data.sort(()=>Math.random()-0.5)

if(order==="reverse")
data.reverse()

quiz=data.slice(0,count)

index=0
correct=0

document.getElementById("setup").style.display="none"
document.getElementById("quiz").style.display="block"

next(direction)

})

}

function next(direction){

if(index>=quiz.length){

alert("終了\n正答率:"+correct/quiz.length)

location.reload()

return
}

let q=quiz[index]

let word,ans

if(direction==="forward"){

word=q[0]
ans=q[1]

}else{

word=q[1]
ans=q[0]

}

document.getElementById("question").innerText=word

let choices=[ans]

while(choices.length<4){

let r=data[Math.floor(Math.random()*data.length)]

let c=(direction==="forward")?r[1]:r[0]

if(!choices.includes(c))
choices.push(c)

}

choices.sort(()=>Math.random()-0.5)

let area=document.getElementById("choices")

area.innerHTML=""

choices.forEach(c=>{

let b=document.createElement("button")

b.className="choice"

b.innerText=c

b.onclick=()=>{

if(c===ans){
correct++
document.getElementById("result").innerText="Correct"
}else{
document.getElementById("result").innerText="Wrong: "+ans
}

index++

setTimeout(()=>next(direction),500)

}

area.appendChild(b)

})

document.getElementById("progress").innerText=
(index+1)+" / "+quiz.length

}
