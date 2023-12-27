function handleSubmit() {
    var button = document.getElementById('getVideosButton');
    button.disabled = true;  // 버튼 비활성화
    button.style.backgroundColor = '#cccccc'; // 버튼을 회색으로 변경
    showLoadingAnimation(); // 로딩 애니메이션 활성화
}

// 페이지 로드 시 enableButton 함수를 호출
window.onload = enableButton;

// 새로고침
function redirectToHome() {
    window.location.href = '/'; // 홈페이지 URL로 리다이렉트
}

function enableButton() {
    var button = document.getElementById('getVideosButton');
    if(button) {
        button.disabled = false;  // 버튼 활성화
        button.style.backgroundColor = ''; // 스타일 초기화
    }
}

function showLoadingAnimation() {
    document.getElementById('loadingAnimation').style.display = 'block';
}

// 자막 다운로드 함수
function downloadSubtitle(channelId, videoId, button) {
    // 버튼 비활성화 및 스타일 변경
    button.disabled = true;
    button.className = 'downloading-button';
    button.innerHTML = 'Downloading...';

    // 로딩 애니메이션 요소 생성 및 추가
    var loader = document.createElement('div');
    loader.className = 'loader-downloading';
    button.parentNode.insertBefore(loader, button.nextSibling);

    fetch(`/download/${channelId}/${videoId}`)
        .then(response => {
            // 다운로드 후 처리

            // 페이지 새로고침
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            button.disabled = false;
            button.className = 'download-link';
            button.innerHTML = 'Download Subtitle';
            loader.remove();
        });
}

// 다운로드한 자막 펼쳐보기
function viewDownload(channelId, videoId) {
    console.log(`Viewing transcription for Channel ID: ${channelId}, Video ID: ${videoId}`);
    window.location.href = `/view-transcription/${channelId}/${videoId}`;
}

// 다운로드 중 다른 행동을 할 때 띄우는 팝업
// <button onclick="confirmDownload()">Download</button>
function confirmDownload() {
    var userResponse = confirm("이미 다른 영상을 다운로드 중입니다. 다운로드를 멈추시겠습니까?");
    if (userResponse) {
        // 사용자가 '네'를 클릭했을 때의 처리
        console.log("다운로드 멈춤");
        alert("확인을 누르셨습니다. 다운로드를 멈췄습니다.");

        // 여기에 다운로드를 멈추는 코드 구현

    } else {
        // 사용자가 '아니오'를 클릭했을 때의 처리
        console.log("다운로드 계속 진행");
        alert("취소를 누르셨습니다. 다운로드를 재개합니다.");
    }
}