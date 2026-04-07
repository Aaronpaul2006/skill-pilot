// gamification_toasts.js
const style = document.createElement('style');
style.textContent = `
    .gt-container { position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; }
    .gt-toast { background: #1a1a26; border: 1px solid #2a2a3d; border-radius: 12px; padding: 16px 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); color: white; font-family: 'DM Sans', sans-serif; display: flex; align-items: center; gap: 16px; animation: gtSlideIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; transform-origin: center right; }
    .gt-toast.fade-out { animation: gtFadeOut 0.3s ease forwards; }
    
    @keyframes gtSlideIn { from { transform: translateX(120%) scale(0.9); opacity: 0; } to { transform: translateX(0) scale(1); opacity: 1; } }
    @keyframes gtFadeOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
    
    .gt-icon-wrap { font-size: 2rem; animation: gtBounce 2s infinite ease-in-out; }
    @keyframes gtBounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
    
    .gt-body h4 { margin: 0 0 4px 0; font-family: 'Syne', sans-serif; font-size: 1rem; color: #e8e8f0; }
    .gt-body p { margin: 0; font-size: 0.85rem; color: #a78bfa; font-weight: 700; }
    
    .gt-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 10000; display: flex; flex-direction: column; align-items: center; justify-content: center; animation: gtFadeIn 0.3s ease; }
    @keyframes gtFadeIn { from { opacity: 0; } to { opacity: 1; } }
    .gt-level-text { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 5rem; background: linear-gradient(135deg, #6c63ff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; animation: gtPop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
    @keyframes gtPop { 0% { transform: scale(0.5); } 100% { transform: scale(1); } }
    .gt-rank-text { font-family: 'Syne', sans-serif; font-size: 2rem; color: white; margin-top: 10px; }
`;
document.head.appendChild(style);

const toastContainer = document.createElement('div');
toastContainer.className = 'gt-container';
document.body.appendChild(toastContainer);

function createToast(icon, title, subtitle, borderColor) {
    const el = document.createElement('div');
    el.className = 'gt-toast';
    if(borderColor) el.style.borderLeft = `4px solid ${borderColor}`;
    
    el.innerHTML = `
        <div class="gt-icon-wrap">${icon}</div>
        <div class="gt-body">
            <h4>${title}</h4>
            <p>${subtitle}</p>
        </div>
    `;
    toastContainer.appendChild(el);
    
    setTimeout(() => {
        el.classList.add('fade-out');
        setTimeout(() => el.remove(), 300);
    }, 4000);
}

window.showXPToast = function(xpAmount) {
    createToast('⭐', 'XP Earned!', `+${xpAmount} XP`, '#43e97b');
};

window.showBadgeToast = function(emoji, name, rarity) {
    const colors = { 'common': '#888899', 'rare': '#6c63ff', 'epic': '#ff6584', 'legendary': '#f7971e' };
    createToast(emoji, 'Badge Earned!', name, colors[rarity] || '#6c63ff');
};

window.showChallengeToast = function(title, xpReward) {
    createToast('🎯', 'Challenge Complete!', `${title} (+${xpReward} XP)`, '#f7971e');
};

window.showLevelUpToast = function(newLevel, rankName) {
    const overlay = document.createElement('div');
    overlay.className = 'gt-overlay';
    overlay.innerHTML = `
        <h1 class="gt-level-text">LEVEL UP!</h1>
        <div class="gt-rank-text">Level ${newLevel} — <span style="color:#43e97b;">${rankName}</span></div>
    `;
    document.body.appendChild(overlay);
    
    setTimeout(() => {
        overlay.style.opacity = '0';
        overlay.style.transition = 'opacity 0.5s ease';
        setTimeout(() => overlay.remove(), 500);
    }, 3500);
};

window.handleGamificationResponse = function(data) {
    if (data.gamification) {
        const g = data.gamification;
        if (g.xp_awarded) setTimeout(() => window.showXPToast(g.xp_awarded), 500);
        if (g.leveled_up) setTimeout(() => window.showLevelUpToast(g.new_level, g.new_rank), 1500);
        if (g.new_badges) {
            g.new_badges.forEach((b, i) => setTimeout(() => window.showBadgeToast(b.emoji, b.name, b.rarity), 1000 + (i * 500)));
        }
        if (g.completed_challenges) {
            g.completed_challenges.forEach((c, i) => setTimeout(() => window.showChallengeToast(c.title, c.xp_reward), 2000 + (i * 500)));
        }
    }
};
