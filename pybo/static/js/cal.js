// 선택된 날짜를 저장하는 변수
let selectedDate = null;
let date = new Date();

const renderCalendar = () => {
    const viewYear = date.getFullYear();
    const viewMonth = date.getMonth();

    document.querySelector('.year-month').textContent = `${viewYear}년 ${viewMonth + 1}월`;

    const prevLast = new Date(viewYear, viewMonth, 0);
    const thisLast = new Date(viewYear, viewMonth + 1, 0);

    const PLDate = prevLast.getDate();
    const PLDay = prevLast.getDay();

    const TLDate = thisLast.getDate();
    const TLDay = thisLast.getDay();

    const prevDates = [];
    const thisDates = [...Array(TLDate + 1).keys()].slice(1);
    const nextDates = [];

    if (PLDay !== 6) {
        for (let i = 0; i < PLDay + 1; i++) {
            prevDates.unshift(PLDate - i);
        }
    }
    for (let i = 1; i < 7 - TLDay; i++) {
        nextDates.push(i);
    }

    const dates = prevDates.concat(thisDates, nextDates);

    const firstDateIndex = dates.indexOf(1);
    const lastDateIndex = dates.lastIndexOf(TLDate);

    dates.forEach((date, i) => {
        const condition = i >= firstDateIndex && i < lastDateIndex + 1 ? 'this' : 'other';
        // 날짜 요소를 클릭 가능한 div 요소로 변경
        dates[i] = `<div class="date ${condition}" data-date="${date}" onclick="handleDateClick(${date})">${date}</div>`;
    });

    document.querySelector('.dates').innerHTML = dates.join('');

    const today = new Date();
    if (viewMonth === today.getMonth() && viewYear === today.getFullYear()) {
        for (let dateElement of document.querySelectorAll('.this')) {
            if (+dateElement.innerText === today.getDate()) {
                dateElement.classList.add('today');
                break;
            }
        }
    }

    // 각 날짜 요소에 이벤트 리스너 추가
    document.querySelectorAll('.this').forEach(dateElement => {
        dateElement.addEventListener('click', function () {
            const day = parseInt(this.innerText); // 클릭된 날짜
            selectedDate = new Date(viewYear, viewMonth, day); // 클릭된 날짜를 저장
            updateDisplayedDate(selectedDate); // 선택된 날짜를 표시
        });

        // 마우스 포인터가 날짜 요소에 들어갔을 때 동작
        dateElement.addEventListener('mouseenter', function () {
            this.classList.add('hover');
        });

        // 마우스 포인터가 날짜 요소에서 나갔을 때 동작
        dateElement.addEventListener('mouseleave', function () {
            this.classList.remove('hover');
        });
    });
};

// 날짜를 클릭했을 때 호출되는 함수
function updateDisplayedDate(selectedDate) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const formattedDate = selectedDate.toLocaleDateString('ko-KR', options);
    const dateElement = document.querySelector('.DS .container #date');
    dateElement.textContent = formattedDate; // 텍스트 콘텐츠로 설정

    // 날짜를 가로로 정렬하기 위해 flex를 사용하여 부모 요소를 가로로 배치합니다.
    dateElement.parentElement.style.display = 'flex';
    dateElement.parentElement.style.alignItems = 'center'; // 세로 가운데 정렬

    // 선택된 날짜의 일정만을 보여주는 함수 호출
    showSelectedDateEvents(selectedDate);
}

// 일정 삭제 함수
function deleteEvent(description, selectedDate, li) {
    fetch('/auth/delete_event/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            description: description,
            date: selectedDate.toISOString().split('T')[0]
        })
    }).then(response => response.json()).then(data => {
        if (data.success) {
            li.remove(); // 성공적으로 삭제되면 리스트 아이템을 삭제합니다.
        } else {
            alert(data.message); // 오류 메시지 출력
        }
    });
}

// 일정 추가 함수 수정
function addEvent(description, selectedDate) {
    const todoList = document.querySelector(".todo-box");
    const li = document.createElement("li");
    const span = document.createElement("span");
    const delBtn = document.createElement("button");
    delBtn.innerText = "X";


    span.innerHTML = description;
    li.appendChild(span);
    li.appendChild(delBtn);

    todoList.appendChild(li);

    delBtn.addEventListener("click", function () {
        deleteEvent(description, selectedDate, li);
    });

    fetch('/auth/add_event/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            description: description,
            date: selectedDate.toISOString().split('T')[0]
        })
    }).then(response => response.json()).then(data => {
        if (!data.success) {
            alert(data.message);
        }
    });
}

// 일정 목록 초기화 및 이벤트 추가
function showSelectedDateEvents(selectedDate) {
    const todoList = document.querySelector(".todo-box");
    todoList.innerHTML = "";

    fetch(`/auth/get_events/?date=${selectedDate.toISOString().split('T')[0]}`)
        .then(response => response.json())
        .then(data => {
            data.events.forEach(event => {
                addEvent(event.description, new Date(event.date));
            });
        });
}

// 일정 목록
const events = [];

const prevMonth = () => {
    date.setMonth(date.getMonth() - 1);
    renderCalendar();
};

const nextMonth = () => {
    date.setMonth(date.getMonth() + 1);
    renderCalendar();
};

const goToday = () => {
    date = new Date();
    renderCalendar();
    updateDisplayedDate(date);
};

document.addEventListener('DOMContentLoaded', () => {
    renderCalendar();

    // 오늘 날짜로 초기화
    const today = new Date();
    updateDisplayedDate(today);

    // 할 일 추가 폼 제출 이벤트 리스너 추가
    document.getElementById("todo-form").addEventListener("submit", function (e) {
        e.preventDefault();
        const todoInput = document.getElementById("whattodo");
        const description = todoInput.value;
        if (!description) {
            alert("할 일을 입력해주세요.");
            return;
        }
        if (!selectedDate) {
            alert("날짜를 선택해주세요.");
            return;
        }
        events.push({ description, date: selectedDate }); // 일정 목록에 추가
        addEvent(description, selectedDate); // 화면에 일정 추가
        todoInput.value = "";
    });
});