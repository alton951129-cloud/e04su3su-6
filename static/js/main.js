document.addEventListener('DOMContentLoaded', () => {
    // 簡單的點擊事件提示，之後可換成實際的路由跳轉
    const loginBtn = document.getElementById('loginBtn');
    if(loginBtn) {
        loginBtn.addEventListener('click', () => {
            alert('登入/註冊功能開發中 (F-05) !');
        });
    }

    const startBtn = document.getElementById('startBtn');
    if(startBtn) {
        startBtn.addEventListener('click', () => {
            const featuresSection = document.getElementById('features');
            featuresSection.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // 視差效果與滑動動畫 (可選增加互動性)
    const cards = document.querySelectorAll('.feature-card');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        card.style.opacity = 0;
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(card);
    });
});
