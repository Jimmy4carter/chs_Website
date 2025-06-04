console.log('hello quiz')
const url = window.location.href

const quizBox = document.getElementById('quiz-box')
const scoreBox = document.getElementById('score-box')
const resultBox = document.getElementById('result-box')
const timerBox = document.getElementById('timerBox')

const activateTimer = (time) => {
    if (time.toString().length < 2){
        timerBox.innerHTML = `<b>0${time}:00</b>`
    }
    else{
        timerBox.innerHTML = `<b>${time}:00</b>`
    }
    let minutes = time - 1
    let seconds = 60
    let displayseconds
    let displayminutes
    const timer = setInterval(()=>{
        seconds --
        if(seconds< 0) {
            seconds = 59
            minutes --

        }
        if(minutes.toString().lenght < 2){
            displayminutes = '0'+minutes
        } else {
            displayminutes = minutes
        }
        if(seconds.toString().length < 2){
            displayseconds = '0' + seconds
        }else{
            displayseconds = seconds
        }
        if( minutes === 0 && seconds === 0) {
            timerBox.innerHTML = "<b>00:00</b>"
            setTimeout(()=>{
                clearInterval(timer)
                alert('Timer over')
                sendData()
            },500) 
        }
        
        timerBox.innerHTML = `<b>${displayminutes}:${displayseconds}`
    }, 1000)
}


$.ajax({
    type: 'GET',
    url: `${url}data`,
    success: function(response){
        const data = response.data
        data.forEach(el => {
            for (const [question, answers] of Object.entries(el)){
                // out of array of questions
                quizBox.innerHTML +=`
                    <hr>
                    <div class="mb-2">
                        <b>${question}</b>
                    </div>
                `
                answers.forEach(answer=>{
                    // output in array of answers
                    quizBox.innerHTML +=`
                        <div>
                            <input type="radio" class="ans" id="${question}-${answer}" name="${question}" value="${answer}">
                            <label for="${question}">${answer}</label>
                        </div>
                    `
                })
            }
        });
        activateTimer(response.time)
    },
    error: function(error){
        console.log(error)
    }
})

const quizForm = document.getElementById('quiz-form')
const csrf = document.getElementsByName('csrfmiddlewaretoken')


const sendData = () => {
    const elements = [...document.getElementsByClassName('ans')]
    const data = {}
    data['csrfmiddlewaretoken'] = csrf[0].value
    elements.forEach(el=>{
        if (el.checked) {
            data[el.name] = el.value
        } else {
            if (!data[el.name]) {
                data[el.name] = null
            }
        }
    })

    $.ajax({
        type: 'POST',
        url: `${url}save/`,
        data: data,
        success: function(response){
            const results =response.results
            console.log(results)
            quizForm.classList.add('invisible')

            scoreBox.innerHTML = `${response.passed ? 'Congratulations! ' : 'Oops..:( '}Your score is ${response.score.toFixed(2)}`

            results.forEach(res=>{
                const resDiv = document.createElement("div")
                for (const [question, resp] of Object.entries(res)){
                    resDiv.innerHTML += question
                    const cls = ['container', 'p-3', 'text-light', 'h3']
                    resDiv.classList.add(...cls)

                    if (resp=='not answered'){
                        resDiv.innerHTML += '- not answered'
                        resDiv.classList.add('bg-danger') 
                    }
                    else{
                        const answer = resp['answered']
                        const correct = resp['correct_answer']

                        if (answer == correct){
                            resDiv.classList.add('bg-success')
                            resDiv.innerHTML += ` answered: ${answer}`
                        }
                        else{
                            resDiv.classList.add('bg-danger')
                            resDiv.innerHTML += ` | correct answer: ${correct}`
                            resDiv.innerHTML == ` | answered: ${answer}`
                        }
                    }
                }
                // const body = document.getElementsByTagName('SECTION')[0]
                resultBox.append(resDiv)
            })
        },
        error: function(error){
            console.log(error)
        }
    })
}

quizForm.addEventListener('submit', e=>{
    e.preventDefault()

    sendData()
})
