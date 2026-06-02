document.addEventListener('DOMContentLoaded', () => {
    // 登入/註冊按鈕事件
    const loginBtn = document.getElementById('loginBtn');
    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            alert('登入/註冊功能開發中 (F-05) !');
        });
    }

    // 立即開始分析按鈕平滑滾動至統計分析中心
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            const analysisSection = document.getElementById('analysis');
            if (analysisSection) {
                analysisSection.scrollIntoView({ behavior: 'smooth' });
            }
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

    // ==========================================================================
    // 統計號碼功能 (F-01 / F-03) 核心 JS 邏輯
    // ==========================================================================

    let frequencyChartInstance = null; // 儲存 Chart.js 實例，切換時需銷毀重建

    // 取得彩券相關配色
    function getGameColors(game) {
        if (game === 'big_lotto') {
            return {
                primary: '#3b82f6',
                gradientStart: 'rgba(59, 130, 246, 0.8)',
                gradientStop: 'rgba(59, 130, 246, 0.1)',
                ballClass: 'ball-lotto-normal'
            };
        } else if (game === 'super_lotto') {
            return {
                primary: '#10b981',
                gradientStart: 'rgba(16, 185, 129, 0.8)',
                gradientStop: 'rgba(16, 185, 129, 0.1)',
                ballClass: 'ball-super-normal'
            };
        } else { // daily_cash_539
            return {
                primary: '#fbbf24',
                gradientStart: 'rgba(251, 191, 36, 0.8)',
                gradientStop: 'rgba(251, 191, 36, 0.1)',
                ballClass: 'ball-539-normal'
            };
        }
    }

    // 異步讀取彩券數據與統計分析
    async function loadGameData(gameType) {
        // 設定網格 Data 屬性 (用於 CSS 邊框配色切換)
        const panelGrid = document.querySelector('.stats-panel-grid');
        if (panelGrid) {
            panelGrid.setAttribute('data-game', gameType);
        }

        // 顯示載入動畫 (Spinner)
        const latestBallsContainer = document.getElementById('latestBalls');
        const hotNumbersContainer = document.getElementById('hotNumbers');
        const coldNumbersContainer = document.getElementById('coldNumbers');
        const historyTableBody = document.getElementById('historyTableBody');

        if (latestBallsContainer) latestBallsContainer.innerHTML = '<div class="loading-spinner"></div>';
        if (hotNumbersContainer) hotNumbersContainer.innerHTML = '<div class="loading-spinner"></div>';
        if (coldNumbersContainer) coldNumbersContainer.innerHTML = '<div class="loading-spinner"></div>';
        if (historyTableBody) historyTableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;"><div class="loading-spinner"></div></td></tr>';

        try {
            // 同時請求歷史紀錄與統計分析 API
            const [historyRes, statsRes] = await Promise.all([
                fetch(`/api/lottery/history/${gameType}`),
                fetch(`/api/lottery/stats/${gameType}`)
            ]);

            const historyData = await historyRes.json();
            const statsData = await statsRes.json();

            if (!historyData.success || !statsData.success) {
                throw new Error('獲取數據失敗，請稍後再試。');
            }

            const historyList = historyData.data;
            const stats = statsData;
            const colors = getGameColors(gameType);

            // --------------------------------------------------
            // 1. 渲染最新一期開獎結果
            // --------------------------------------------------
            if (historyList && historyList.length > 0) {
                const latest = historyList[0];
                document.getElementById('latestDrawNo').innerText = `期數: ${latest.draw_number}`;
                document.getElementById('latestDrawDate').innerText = latest.draw_date;

                // 生成球體
                latestBallsContainer.innerHTML = '';
                latest.numbers.forEach(num => {
                    const ball = document.createElement('div');
                    ball.className = `ball ${colors.ballClass}`;
                    ball.innerText = String(num).padStart(2, '0');
                    latestBallsContainer.appendChild(ball);
                });

                // 如果有特別號
                if (latest.special_num !== null) {
                    const specBall = document.createElement('div');
                    specBall.className = 'ball ball-special';
                    specBall.innerText = String(latest.special_num).padStart(2, '0');

                    // 特別號標籤
                    const badge = document.createElement('span');
                    badge.className = 'ball-special-badge';
                    badge.innerText = gameType === 'super_lotto' ? '第二區' : '特別號';
                    specBall.appendChild(badge);

                    latestBallsContainer.appendChild(specBall);
                }
            } else {
                latestBallsContainer.innerHTML = '<div class="error-message">無歷史開獎數據</div>';
            }

            // --------------------------------------------------
            // 2. 渲染冷熱門號碼 (Top 5)
            // --------------------------------------------------
            hotNumbersContainer.innerHTML = '';
            stats.hot_numbers.forEach(num => {
                const badge = document.createElement('span');
                badge.className = 'num-badge hot';
                badge.innerText = String(num).padStart(2, '0');
                hotNumbersContainer.appendChild(badge);
            });

            coldNumbersContainer.innerHTML = '';
            stats.cold_numbers.forEach(num => {
                const badge = document.createElement('span');
                badge.className = 'num-badge cold';
                badge.innerText = String(num).padStart(2, '0');
                coldNumbersContainer.appendChild(badge);
            });

            // --------------------------------------------------
            // 3. 渲染進階指標
            // --------------------------------------------------
            // (a) 奇偶比
            const totalBalls = stats.odd_count + stats.even_count;
            if (totalBalls > 0) {
                const oddPerc = Math.round((stats.odd_count / totalBalls) * 100);
                const evenPerc = 100 - oddPerc;

                const oddPart = document.querySelector('#oddEvenBar .odd-part');
                const evenPart = document.querySelector('#oddEvenBar .even-part');
                
                if (oddPart && evenPart) {
                    oddPart.style.width = `${oddPerc}%`;
                    oddPart.innerText = `${oddPerc}%`;
                    evenPart.style.width = `${evenPerc}%`;
                    evenPart.innerText = `${evenPerc}%`;
                }
                
                document.getElementById('oddEvenRatioText').innerText = 
                    `奇數: ${stats.odd_count} 次 (${oddPerc}%) | 偶數: ${stats.even_count} 次 (${evenPerc}%)`;
            }

            // (b) 平均總和
            document.getElementById('avgSumVal').innerText = stats.average_sum;
            const avgExpectationText = document.getElementById('avgExpectationText');
            if (avgExpectationText) {
                if (gameType === 'big_lotto') {
                    avgExpectationText.innerText = '理論中位數期望值: 150 (對稱分布)';
                } else if (gameType === 'super_lotto') {
                    avgExpectationText.innerText = '理論中位數期望值: 117 (第一區對稱)';
                } else {
                    avgExpectationText.innerText = '理論中位數期望值: 100 (對稱分布)';
                }
            }

            // --------------------------------------------------
            // 4. 渲染開出頻率圖表 (Chart.js)
            // --------------------------------------------------
            renderFrequencyChart(stats.frequencies, gameType, colors);

            // --------------------------------------------------
            // 5. 渲染歷史開獎表格
            // --------------------------------------------------
            historyTableBody.innerHTML = '';
            
            // 調整特別號標題文字
            const tableHeaderRow = document.getElementById('tableHeaderRow');
            if (tableHeaderRow) {
                const specialTh = tableHeaderRow.children[3];
                if (specialTh) {
                    if (gameType === 'daily_cash_539') {
                        specialTh.style.display = 'none';
                    } else {
                        specialTh.style.display = '';
                        specialTh.innerText = gameType === 'super_lotto' ? '第二區' : '特別號';
                    }
                }
            }

            historyList.forEach(draw => {
                const tr = document.createElement('tr');
                
                // 期數
                const tdNo = document.createElement('td');
                tdNo.innerText = draw.draw_number;
                tdNo.style.fontWeight = '700';
                tr.appendChild(tdNo);

                // 日期
                const tdDate = document.createElement('td');
                tdDate.innerText = draw.draw_date;
                tr.appendChild(tdDate);

                // 號碼球清單 (表格內小球)
                const tdBalls = document.createElement('td');
                draw.numbers.forEach(num => {
                    const sBall = document.createElement('span');
                    sBall.className = `num-badge table-ball ${colors.ballClass}`;
                    sBall.innerText = String(num).padStart(2, '0');
                    tdBalls.appendChild(sBall);
                });
                tr.appendChild(tdBalls);

                // 特別號 (如果有)
                if (gameType !== 'daily_cash_539') {
                    const tdSpecial = document.createElement('td');
                    if (draw.special_num !== null) {
                        const sBall = document.createElement('span');
                        sBall.className = 'num-badge table-ball ball-special';
                        sBall.innerText = String(draw.special_num).padStart(2, '0');
                        tdSpecial.appendChild(sBall);
                    } else {
                        tdSpecial.innerText = '-';
                    }
                    tr.appendChild(tdSpecial);
                }

                historyTableBody.appendChild(tr);
            });

        } catch (error) {
            console.error(error);
            const errMsg = `<div class="error-message">⚠️ 載入失敗: ${error.message}</div>`;
            latestBallsContainer.innerHTML = errMsg;
            hotNumbersContainer.innerHTML = errMsg;
            coldNumbersContainer.innerHTML = errMsg;
            historyTableBody.innerHTML = `<tr><td colspan="4" style="text-align:center;" class="error-message">⚠️ 載入失敗: ${error.message}</td></tr>`;
        }
    }

    // 繪製或更新開出頻率圖表
    function renderFrequencyChart(frequencies, gameType, colors) {
        // 先排序數字，確保 X 軸由小到大 (1, 2, 3...)
        const sortedKeys = Object.keys(frequencies).map(Number).sort((a, b) => a - b);
        const labels = sortedKeys.map(k => String(k).padStart(2, '0'));
        const data = sortedKeys.map(k => frequencies[k]);

        const ctx = document.getElementById('frequencyChart').getContext('2d');

        // 銷毀現有圖表
        if (frequencyChartInstance) {
            frequencyChartInstance.destroy();
        }

        // 建立背景漸層
        const gradient = ctx.createLinearGradient(0, 0, 0, 350);
        gradient.addColorStop(0, colors.gradientStart);
        gradient.addColorStop(1, colors.gradientStop);

        // Chart.js 設定
        frequencyChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '開出次數',
                    data: data,
                    backgroundColor: gradient,
                    borderColor: colors.primary,
                    borderWidth: 1.5,
                    borderRadius: 4,
                    hoverBackgroundColor: colors.primary,
                    hoverBorderColor: '#ffffff',
                    hoverBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // 不需要圖例，因為只有一組數據
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#ffffff',
                        bodyColor: '#e2e8f0',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: function(context) {
                                return `號碼 [ ${context[0].label} ]`;
                            },
                            label: function(context) {
                                return `累積開出頻率: ${context.parsed.y} 次`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: {
                                family: "'Inter', 'Noto Sans TC', sans-serif",
                                size: 10,
                                weight: '600'
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: {
                                family: "'Inter', 'Noto Sans TC', sans-serif",
                                size: 11
                            },
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    // ==========================================================================
    // 綁定彩券種類切換按鈕事件
    // ==========================================================================
    const selectorButtons = document.querySelectorAll('.selector-btn');
    selectorButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // 移除其他按鈕的 active 狀態
            selectorButtons.forEach(b => b.classList.remove('active'));
            // 加上 active 狀態
            btn.classList.add('active');

            const game = btn.getAttribute('data-game');
            loadGameData(game);
        });
    });

    // 網頁首次載入，預設載入大樂透數據
    loadGameData('big_lotto');
});
