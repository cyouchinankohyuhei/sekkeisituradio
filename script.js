// --- ローディング画面の制御 ---
const loadingScreen = document.getElementById('loading-screen');
const loadingPercentage = document.getElementById('loading-percentage');

let progress = 0;
let isLoaded = false;

// ページの読み込みが完了したフラグ
window.addEventListener('load', () => {
    isLoaded = true;
});

// チューニングギミック: 0%から100%までカウントアップ
const duration = 1500; // 約1.5秒で100%にする（フェイクアニメーション）
const intervalTime = 30; // 30msごとに更新
const increment = 100 / (duration / intervalTime);

const progressInterval = setInterval(() => {
    progress += increment;
    
    // ページ読み込みが終わっていない場合は99%で寸止め
    if (progress >= 99 && !isLoaded) {
        progress = 99;
    }

    if (progress >= 100) {
        progress = 100;
        clearInterval(progressInterval);
        
        if (loadingPercentage) {
            loadingPercentage.innerText = `100%`;
        }
        
        // 100%になった後、少し余韻を残してフェードアウト
        setTimeout(() => {
            if (loadingScreen) {
                loadingScreen.classList.add('fade-out');
            }
        }, 400); 
    } else {
        if (loadingPercentage) {
            loadingPercentage.innerText = `${Math.floor(progress)}%`;
        }
    }
}, intervalTime);

document.addEventListener('DOMContentLoaded', () => {
    // スムーズスクロール
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            if(!targetId.startsWith('#')) return;
            
            e.preventDefault();
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - (headerHeight || 0) - 20;
  
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // スクロールに応じたフェードインアニメーション
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-in').forEach(section => {
        observer.observe(section);
    });

    // Material Ripple Effect Logic
    const createRipple = (event) => {
        const button = event.currentTarget;
        
        const circle = document.createElement("span");
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;

        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.getBoundingClientRect().left - radius}px`;
        circle.style.top = `${event.clientY - button.getBoundingClientRect().top - radius}px`;
        circle.classList.add("ripple-span");

        // 要素の色に応じてリップルの色味を変更（ボタンは白リップル、それ以外は黒系）
        if(!button.classList.contains('btn-primary') && !button.classList.contains('mdc-fab')) {
            circle.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
        }

        const ripple = button.getElementsByClassName("ripple-span")[0];
        if (ripple) {
            ripple.remove();
        }

        button.appendChild(circle);
    }

    const ripples = document.querySelectorAll('.ripple');
    for (const rippleButton of ripples) {
        rippleButton.addEventListener("mousedown", createRipple);
    }

    // --- 簡易診断ツール (Quiz Modal) Logic ---
    const modalOverlay = document.getElementById('diagnosis-modal');
    const openBtn = document.getElementById('open-diagnosis-btn');
    const closeBtn = document.getElementById('close-diagnosis-btn');
    const quizContainer = document.getElementById('quiz-container');

    const quizData = [
        {
            question: "対象の空き家の状態は？",
            options: [
                "築年数が古く、かなり傷んでいる",
                "比較的きれいで、少し直せば使えそう",
                "大きすぎて持て余している",
                "まだ状態がわからない"
            ]
        },
        {
            question: "空き家がある場所の雰囲気は？",
            options: [
                "住宅地や人が集まるエリア",
                "自然豊かな地方・郊外",
                "商店街や駅の近く"
            ]
        },
        {
            question: "あなたの「想い」に一番近いものは？",
            options: [
                "誰かに貸して、地域の役に立てたい",
                "自分たちの住まいや別荘にしたい",
                "あまりお金をかけずに整理したい",
                "売りたい・手放したい"
            ]
        }
    ];

    let currentStep = 0;
    let answers = [];

    const openModal = () => {
        currentStep = 0;
        answers = [];
        renderQuiz();
        modalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // 背景スクロール防止
    };

    const closeModal = () => {
        modalOverlay.classList.remove('active');
        document.body.style.overflow = '';
    };

    if(openBtn) openBtn.addEventListener('click', openModal);
    if(closeBtn) closeBtn.addEventListener('click', closeModal);
    if(modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if(e.target === modalOverlay) closeModal();
        });
    }

    const renderQuiz = () => {
        if (currentStep < quizData.length) {
            const currentQ = quizData[currentStep];
            let optionsHtml = '';
            
            currentQ.options.forEach((opt, index) => {
                optionsHtml += `
                    <button class="quiz-option-btn ripple" onclick="window.selectAnswer(${index})">
                        <span class="quiz-option-number">Q${index + 1}</span>
                        <span>${opt}</span>
                    </button>
                `;
            });

            quizContainer.innerHTML = `
                <div class="quiz-header">
                    <span class="quiz-progress">STEP ${currentStep + 1} / ${quizData.length}</span>
                    <h3 class="quiz-question">${currentQ.question}</h3>
                </div>
                <div class="quiz-options">
                    ${optionsHtml}
                </div>
            `;
            // 再度リップルをつける
            const newRipples = quizContainer.querySelectorAll('.ripple');
            newRipples.forEach(btn => btn.addEventListener('mousedown', createRipple));
        } else {
            showResult();
        }
    };

    window.selectAnswer = (index) => {
        answers.push(index);
        currentStep++;
        
        // 少しディレイを入れて画面切り替え（UX向上）
        quizContainer.style.opacity = 0;
        setTimeout(() => {
            renderQuiz();
            quizContainer.style.opacity = 1;
        }, 200);
    };

    const showResult = () => {
        // 結果ロジック: 最後の質問メインで判定する簡易版
        const lastAns = answers[2];
        let result = {};
        
        if (lastAns === 0) {
            result = {
                type: '地域貢献・コミュニティ系',
                title: 'シェアスペースやカフェへのリノベーション',
                desc: '地域の人々が集まる拠点としての活用にぴったりです。想いのこもった建物を、新しいコミュニティの場として生まれ変わらせませんか？事業計画からサポートいたします。'
            };
        } else if (lastAns === 1) {
            result = {
                type: '居住・別荘系',
                title: 'ご自身のためのフルリノベーション',
                desc: '古い建物の味わいを活かしつつ、今のライフスタイルに合わせた快適な住まいへ。素材選びからこだわり、世界に一つの特別な空間を一緒につくりましょう。'
            };
        } else if (lastAns === 2 || lastAns === 3) {
            result = {
                type: '整理・売却サポート系',
                title: '負担を減らすための売却・活用診断',
                desc: '無理に活用せず、次の方へバトンタッチするのも立派な選択です。リノベーションを前提とした物件としての査定や、そのまま賃貸に出す最小限の改修など、負担の少ない方法をご提案します。'
            };
        } else {
             result = {
                type: '自由活用系',
                title: 'まずは現地調査でポテンシャルチェック',
                desc: '現地にお伺いし、建物の状態や周辺環境から一番「無理のない」活用方法をご提案します。'
            };
        }

        quizContainer.innerHTML = `
            <div class="quiz-result fade-in visible">
                <div class="quiz-result-type">${result.type}</div>
                <h3 class="quiz-result-title">${result.title}</h3>
                <p class="quiz-result-desc">${result.desc}</p>
                <div style="text-align: center;">
                    <button class="btn btn-primary btn-large ripple" style="width: 100%; justify-content: center;" onclick="document.getElementById('close-diagnosis-btn').click(); document.querySelector('#contact').scrollIntoView({behavior:'smooth'}); setTimeout(()=>document.getElementById('property').selectedIndex=1, 500);">
                        <span class="material-symbols-rounded">mail</span>
                        この結果について相談する
                    </button>
                </div>
            </div>
        `;
        const newRipples = quizContainer.querySelectorAll('.ripple');
        newRipples.forEach(btn => btn.addEventListener('mousedown', createRipple));
    };

    // --- お問い合わせフォーム (Web3Forms Ajax送信) ---
    const contactForm = document.getElementById('contact-form');
    const formResult = document.getElementById('form-result');
    const submitBtn = document.getElementById('submit-btn');

    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Web3Formsのアクセスキーが設定されているかチェック
            const accessKey = document.getElementById('access_key').value;
            if (accessKey === 'YOUR_ACCESS_KEY_HERE') {
                alert('【準備中】\nWeb3Formsのアクセスキーがまだ設定されていません。\nチャットでアクセスキーをお伝えください！');
                return;
            }

            const formData = new FormData(contactForm);
            const object = Object.fromEntries(formData);
            const json = JSON.stringify(object);

            formResult.style.display = 'block';
            formResult.style.color = 'var(--md-sys-color-primary)';
            formResult.innerHTML = '送信中...';
            submitBtn.disabled = true;

            fetch('https://api.web3forms.com/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: json
            })
            .then(async (response) => {
                let json = await response.json();
                if (response.status == 200) {
                    formResult.style.color = 'green';
                    formResult.innerHTML = 'お便りが送信されました。お返事まで少々お待ちください。';
                    contactForm.reset();
                } else {
                    console.log(response);
                    formResult.style.color = 'red';
                    formResult.innerHTML = json.message || '送信に失敗しました。時間をおいて再度お試しください。';
                }
            })
            .catch(error => {
                console.log(error);
                formResult.style.color = 'red';
                formResult.innerHTML = '送信に失敗しました。通信環境をご確認ください。';
            })
            .then(function() {
                submitBtn.disabled = false;
                setTimeout(() => {
                    formResult.style.display = 'none';
                }, 8000);
            });
        });
    }
});
