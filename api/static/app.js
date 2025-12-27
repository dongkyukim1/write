/**
 * Script Studio - Main Application
 * 대본 작성 AI 시스템 웹 UI
 */

// API Base URL
const API_BASE = '';

// State
let state = {
    projects: [],
    currentProject: null,
    currentEpisode: null,
    currentScene: null,
    characters: [],
    episodes: [],
    generatedContent: null,
    synopsis: null
};

// ==================== API Functions ====================

async function api(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API 요청 실패');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', async () => {
    await loadProjects();
    checkServerStatus();
});

async function checkServerStatus() {
    try {
        await api('/health');
        document.querySelector('.status-dot').style.background = 'var(--success)';
    } catch {
        document.querySelector('.status-dot').style.background = 'var(--error)';
    }
}

// ==================== Project Functions ====================

async function loadProjects() {
    try {
        state.projects = await api('/api/projects/');
        renderProjectList();
    } catch (error) {
        console.error('Failed to load projects:', error);
    }
}

function renderProjectList() {
    const container = document.getElementById('project-list');
    
    if (state.projects.length === 0) {
        container.innerHTML = `
            <div class="empty-list">
                <p style="color: var(--text-tertiary); font-size: 13px; padding: 12px;">
                    프로젝트가 없습니다
                </p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.projects.map(project => `
        <div class="project-item ${state.currentProject?.id === project.id ? 'active' : ''}" 
             onclick="selectProject(${project.id})">
            <span class="icon">📁</span>
            <span class="name">${escapeHtml(project.title)}</span>
        </div>
    `).join('');
}

async function selectProject(projectId) {
    try {
        state.currentProject = await api(`/api/projects/${projectId}`);
        state.currentEpisode = null;
        state.currentScene = null;
        
        // 캐릭터와 에피소드 로드
        await Promise.all([
            loadCharacters(projectId),
            loadEpisodes(projectId)
        ]);
        
        renderProjectList();
        showProjectView();
    } catch (error) {
        console.error('Failed to select project:', error);
    }
}

function showProjectView() {
    document.getElementById('empty-state').style.display = 'none';
    document.getElementById('project-view').style.display = 'block';
    document.getElementById('scene-view').style.display = 'none';
    
    const project = state.currentProject;
    
    // 브레드크럼
    document.getElementById('breadcrumb').textContent = project.title;
    
    // 통계
    document.getElementById('stat-episodes').textContent = project.statistics?.total_episodes || 0;
    document.getElementById('stat-scenes').textContent = project.statistics?.total_scenes || 0;
    document.getElementById('stat-characters').textContent = project.statistics?.total_characters || 0;
    document.getElementById('stat-words').textContent = formatNumber(project.statistics?.total_words || 0);
    
    // 세계관 & 스타일
    document.getElementById('world-setting').textContent = project.world_setting || '설정되지 않음';
    document.getElementById('style-guide').textContent = project.style_guide || '설정되지 않음';
    
    // 탭 초기화
    switchTab('overview');
}

function showNewProjectModal() {
    document.getElementById('modal-new-project').classList.add('active');
}

async function createProject() {
    const title = document.getElementById('new-project-title').value.trim();
    const projectType = document.getElementById('new-project-type').value;
    const description = document.getElementById('new-project-desc').value.trim();
    const worldSetting = document.getElementById('new-project-world').value.trim();
    
    if (!title) {
        showToast('프로젝트 제목을 입력하세요', 'error');
        return;
    }
    
    try {
        const result = await api('/api/projects/', {
            method: 'POST',
            body: JSON.stringify({
                title,
                project_type: projectType,
                description,
                world_setting: worldSetting
            })
        });
        
        showToast('프로젝트가 생성되었습니다');
        closeModal('modal-new-project');
        
        // 폼 초기화
        document.getElementById('new-project-title').value = '';
        document.getElementById('new-project-desc').value = '';
        document.getElementById('new-project-world').value = '';
        
        await loadProjects();
        await selectProject(result.id);
    } catch (error) {
        console.error('Failed to create project:', error);
    }
}

// ==================== Character Functions ====================

async function loadCharacters(projectId) {
    try {
        state.characters = await api(`/api/characters/by-project/${projectId}`);
        renderCharacterList();
        renderCharacterCheckboxes();
    } catch (error) {
        console.error('Failed to load characters:', error);
    }
}

function renderCharacterList() {
    const container = document.getElementById('character-list');
    
    if (state.characters.length === 0) {
        container.innerHTML = `
            <div class="empty-list" style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <p style="color: var(--text-tertiary);">캐릭터가 없습니다</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.characters.map(char => `
        <div class="character-card">
            <div class="character-header">
                <div class="character-avatar">${char.name.charAt(0)}</div>
                <div class="character-info">
                    <h4>${escapeHtml(char.name)}</h4>
                    <span class="character-role">${getRoleName(char.role)}</span>
                </div>
            </div>
            <p class="character-desc">${escapeHtml(char.description || '설명 없음')}</p>
        </div>
    `).join('');
}

function renderCharacterCheckboxes() {
    const container = document.getElementById('gen-characters');
    
    container.innerHTML = state.characters.map(char => `
        <div class="checkbox-item" data-id="${char.id}" onclick="toggleCharacter(this)">
            <input type="checkbox" value="${char.id}" style="display: none;">
            ${escapeHtml(char.name)}
        </div>
    `).join('');
}

function toggleCharacter(element) {
    element.classList.toggle('selected');
    const checkbox = element.querySelector('input');
    if (checkbox) {
        checkbox.checked = element.classList.contains('selected');
    }
}

function showNewCharacterModal() {
    document.getElementById('modal-new-character').classList.add('active');
}

async function createCharacter() {
    const name = document.getElementById('new-char-name').value.trim();
    const role = document.getElementById('new-char-role').value;
    const personality = document.getElementById('new-char-personality').value.trim();
    const speechPattern = document.getElementById('new-char-speech').value.trim();
    const forbidden = document.getElementById('new-char-forbidden').value.trim();
    
    if (!name) {
        showToast('캐릭터 이름을 입력하세요', 'error');
        return;
    }
    
    try {
        await api('/api/characters/', {
            method: 'POST',
            body: JSON.stringify({
                project_id: state.currentProject.id,
                name,
                role,
                personality_description: personality,
                speech_pattern: speechPattern,
                forbidden_actions: forbidden ? forbidden.split('\n').filter(s => s.trim()) : []
            })
        });
        
        showToast('캐릭터가 추가되었습니다');
        closeModal('modal-new-character');
        
        // 폼 초기화
        document.getElementById('new-char-name').value = '';
        document.getElementById('new-char-personality').value = '';
        document.getElementById('new-char-speech').value = '';
        document.getElementById('new-char-forbidden').value = '';
        
        await loadCharacters(state.currentProject.id);
    } catch (error) {
        console.error('Failed to create character:', error);
    }
}

// ==================== Episode Functions ====================

async function loadEpisodes(projectId) {
    try {
        state.episodes = await api(`/api/episodes/by-project/${projectId}`);
        renderEpisodeList();
        renderEpisodeSelect();
    } catch (error) {
        console.error('Failed to load episodes:', error);
    }
}

function renderEpisodeList() {
    const container = document.getElementById('episode-list');
    
    if (state.episodes.length === 0) {
        container.innerHTML = `
            <div class="empty-list" style="text-align: center; padding: 40px;">
                <p style="color: var(--text-tertiary);">에피소드가 없습니다</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.episodes.map(ep => `
        <div class="episode-item" onclick="selectEpisode(${ep.id})">
            <div class="episode-header">
                <span class="episode-number">EP ${ep.episode_number}</span>
                <span class="episode-meta">${ep.scene_count || 0}개 장면</span>
            </div>
            <div class="episode-title">${escapeHtml(ep.title)}</div>
            ${ep.main_topic ? `<div class="episode-meta">${escapeHtml(ep.main_topic)}</div>` : ''}
        </div>
    `).join('');
}

function renderEpisodeSelect() {
    const select = document.getElementById('gen-episode');
    
    select.innerHTML = `
        <option value="">에피소드를 선택하세요</option>
        ${state.episodes.map(ep => `
            <option value="${ep.id}">EP ${ep.episode_number}: ${escapeHtml(ep.title)}</option>
        `).join('')}
    `;
}

async function selectEpisode(episodeId) {
    try {
        state.currentEpisode = await api(`/api/episodes/${episodeId}`);
        // 에피소드 상세 뷰 표시 (필요시 구현)
        showToast(`에피소드 ${state.currentEpisode.episode_number} 선택됨`);
    } catch (error) {
        console.error('Failed to select episode:', error);
    }
}

function showNewEpisodeModal() {
    // 다음 에피소드 번호 자동 설정
    const nextNumber = state.episodes.length > 0 
        ? Math.max(...state.episodes.map(e => e.episode_number)) + 1 
        : 1;
    document.getElementById('new-ep-number').value = nextNumber;
    document.getElementById('modal-new-episode').classList.add('active');
}

async function createEpisode() {
    const episodeNumber = parseInt(document.getElementById('new-ep-number').value);
    const title = document.getElementById('new-ep-title').value.trim();
    const mainTopic = document.getElementById('new-ep-topic').value.trim();
    const notes = document.getElementById('new-ep-notes').value.trim();
    
    if (!title) {
        showToast('에피소드 제목을 입력하세요', 'error');
        return;
    }
    
    try {
        await api('/api/episodes/', {
            method: 'POST',
            body: JSON.stringify({
                project_id: state.currentProject.id,
                episode_number: episodeNumber,
                title,
                main_topic: mainTopic,
                notes
            })
        });
        
        showToast('에피소드가 생성되었습니다');
        closeModal('modal-new-episode');
        
        // 폼 초기화
        document.getElementById('new-ep-title').value = '';
        document.getElementById('new-ep-topic').value = '';
        document.getElementById('new-ep-notes').value = '';
        
        await loadEpisodes(state.currentProject.id);
    } catch (error) {
        console.error('Failed to create episode:', error);
    }
}

// ==================== Scene Generation ====================

async function generateScene() {
    const episodeId = document.getElementById('gen-episode').value;
    const sceneNumber = parseInt(document.getElementById('gen-scene-number').value);
    const goal = document.getElementById('gen-goal').value.trim();
    const sceneType = document.getElementById('gen-scene-type').value;
    const conflictType = document.getElementById('gen-conflict').value;
    
    // 선택된 캐릭터
    const selectedChars = Array.from(document.querySelectorAll('#gen-characters .checkbox-item.selected'))
        .map(item => parseInt(item.dataset.id));
    
    if (!episodeId) {
        showToast('에피소드를 선택하세요', 'error');
        return;
    }
    
    if (!goal) {
        showToast('장면 목표를 입력하세요', 'error');
        return;
    }
    
    const btn = document.getElementById('generate-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        // 1. 먼저 장면 메타데이터 저장
        // title은 goal의 첫 줄 또는 전체를 사용
        const title = goal.split('\n')[0].substring(0, 50);
        
        const sceneResult = await api('/api/scenes/', {
            method: 'POST',
            body: JSON.stringify({
                episode_id: parseInt(episodeId),
                scene_number: sceneNumber,
                scene_type: sceneType,
                title: title,
                goal: goal,
                conflict_type: conflictType,
                character_ids: selectedChars,
                content: '[AI 생성 중...]'
            })
        });
        
        showToast('장면 생성 중... AI가 대본을 작성하고 있습니다');
        
        // 2. AI로 실제 대본 생성
        const generateResult = await api('/api/generate/scene', {
            method: 'POST',
            body: JSON.stringify({
                scene_id: sceneResult.id,
                goal: goal,
                scene_type: sceneType,
                conflict_type: conflictType,
                character_ids: selectedChars
            })
        });
        
        // 결과 표시
        state.generatedContent = generateResult;
        document.getElementById('generate-result').style.display = 'block';
        document.getElementById('result-content').textContent = generateResult.content;
        
        showToast(`대본이 생성되었습니다! (${generateResult.word_count}자)`);
        
        // 에피소드 목록 새로고침
        await loadEpisodes(state.currentProject.id);
        
    } catch (error) {
        console.error('Failed to generate scene:', error);
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

function copyResult() {
    const content = document.getElementById('result-content').textContent;
    navigator.clipboard.writeText(content);
    showToast('클립보드에 복사되었습니다');
}

async function saveScene() {
    if (!state.generatedContent) return;
    showToast('장면이 저장되었습니다');
}

// ==================== UI Functions ====================

function switchTab(tabName) {
    // 탭 버튼 업데이트
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    
    // 탭 컨텐츠 업데이트
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabName}`);
    });
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.style.background = type === 'error' ? 'var(--error)' : 'var(--text-primary)';
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ==================== Utility Functions ====================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatNumber(num) {
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + '만';
    }
    return num.toLocaleString();
}

function getRoleName(role) {
    const roles = {
        'host': '진행자',
        'co_host': '공동 진행자',
        'guest': '게스트',
        'protagonist': '주인공',
        'antagonist': '적대자',
        'supporting': '조연',
        'narrator': '나레이터'
    };
    return roles[role] || role;
}

// ==================== Scene View Functions ====================

async function goBackToEpisode() {
    document.getElementById('scene-view').style.display = 'none';
    document.getElementById('project-view').style.display = 'block';
    switchTab('episodes');
}

async function saveCurrentScene() {
    if (!state.currentScene) return;
    
    const title = document.getElementById('scene-title').value;
    const content = document.getElementById('scene-content').value;
    
    try {
        await api(`/api/scenes/${state.currentScene.id}`, {
            method: 'PUT',
            body: JSON.stringify({
                title,
                content,
                human_edited: true
            })
        });
        
        showToast('장면이 저장되었습니다');
    } catch (error) {
        console.error('Failed to save scene:', error);
    }
}

async function evaluateCurrentScene() {
    if (!state.currentScene) return;
    
    const content = document.getElementById('scene-content').value;
    
    if (!content.trim()) {
        showToast('평가할 내용이 없습니다', 'error');
        return;
    }
    
    showToast('평가 기능은 MCP 서버를 통해 사용하세요');
}

// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
});

// ==================== 생성된 대본 탭 Functions ====================

let allScenes = [];
let selectedSceneId = null;

async function loadAllScenes() {
    if (!state.currentProject) return;
    
    try {
        // 모든 에피소드의 장면 로드
        allScenes = [];
        for (const ep of state.episodes) {
            const scenes = await api(`/api/episodes/${ep.id}/scenes`);
            allScenes.push(...scenes.map(s => ({ ...s, episode: ep })));
        }
        
        renderScriptsList();
        updateScriptsEpisodeFilter();
    } catch (error) {
        console.error('Failed to load scenes:', error);
    }
}

function updateScriptsEpisodeFilter() {
    const select = document.getElementById('scripts-episode-filter');
    select.innerHTML = `
        <option value="">모든 에피소드</option>
        ${state.episodes.map(ep => `
            <option value="${ep.id}">EP ${ep.episode_number}: ${escapeHtml(ep.title)}</option>
        `).join('')}
    `;
}

function loadScriptsByEpisode() {
    renderScriptsList();
}

function renderScriptsList() {
    const container = document.getElementById('scripts-list');
    const filterValue = document.getElementById('scripts-episode-filter').value;
    
    let filteredScenes = allScenes;
    if (filterValue) {
        filteredScenes = allScenes.filter(s => s.episode.id === parseInt(filterValue));
    }
    
    if (filteredScenes.length === 0) {
        container.innerHTML = `
            <div class="empty-scripts">
                <div class="empty-scripts-icon">📝</div>
                <h4>생성된 장면이 없습니다</h4>
                <p>AI 생성 탭에서 새로운 장면을 만들어보세요</p>
            </div>
        `;
        document.getElementById('script-detail').style.display = 'none';
        return;
    }
    
    container.innerHTML = filteredScenes.map(scene => `
        <div class="script-item ${selectedSceneId === scene.id ? 'active' : ''}" 
             onclick="selectScript(${scene.id}, this)">
            <div class="script-number">${scene.scene_number}</div>
            <div class="script-info">
                <h4>${escapeHtml(scene.title || `장면 ${scene.scene_number}`)}</h4>
                <p>EP${scene.episode.episode_number} · ${getSceneTypeName(scene.scene_type)} · ${scene.word_count || 0}자</p>
            </div>
            <div class="script-badges">
                ${scene.ai_generated ? '<span class="badge">AI</span>' : ''}
                ${scene.human_edited ? '<span class="badge">수정됨</span>' : ''}
            </div>
            ${scene.has_evaluation ? `
                <div class="script-score ${getScoreClass(scene.overall_score)}">
                    ${Math.round((scene.overall_score || 0) * 100)}점
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function selectScript(sceneId, element) {
    selectedSceneId = sceneId;
    
    // 목록에서 active 표시
    document.querySelectorAll('.script-item').forEach(item => {
        item.classList.remove('active');
    });
    if (element) element.classList.add('active');
    
    try {
        // 장면 상세 정보 로드
        const scene = await api(`/api/scenes/${sceneId}`);
        
        // 상세 뷰 표시
        const detailPanel = document.getElementById('script-detail');
        detailPanel.style.display = 'block';
        
        // 메타 정보
        document.getElementById('detail-scene-type').textContent = getSceneTypeName(scene.scene_type);
        document.getElementById('detail-ai-badge').style.display = scene.ai_generated ? 'inline' : 'none';
        document.getElementById('detail-edited-badge').style.display = scene.human_edited ? 'inline' : 'none';
        document.getElementById('detail-scene-title').textContent = scene.title || `장면 ${scene.scene_number}`;
        document.getElementById('detail-scene-goal').textContent = scene.goal || '';
        
        // 본문
        document.getElementById('detail-scene-content').textContent = scene.content || '(내용 없음)';
        
        // 평가 정보 로드 (평가가 없으면 조용히 숨김)
        try {
            const evalResponse = await fetch(`/api/evaluations/by-scene/${sceneId}`);
            if (evalResponse.ok) {
                const evaluation = await evalResponse.json();
                showEvaluationDetail(evaluation);
            } else {
                document.getElementById('detail-evaluation').style.display = 'none';
            }
        } catch {
            document.getElementById('detail-evaluation').style.display = 'none';
        }
        
    } catch (error) {
        console.error('Failed to load scene detail:', error);
    }
}

function showEvaluationDetail(evaluation) {
    const panel = document.getElementById('detail-evaluation');
    panel.style.display = 'block';
    
    // 점수 표시 (API 응답 구조에 맞춤)
    const scores = evaluation.scores || {};
    const scoreItems = [
        { id: 'overall', value: scores.overall || 0 },
        { id: 'creativity', value: scores.creativity || 0 },
        { id: 'consistency', value: scores.consistency || 0 },
        { id: 'emotion', value: scores.emotion || 0 },
        { id: 'dialogue', value: scores.dialogue || 0 }
    ];
    
    scoreItems.forEach(score => {
        const pct = Math.round(score.value * 100);
        document.getElementById(`eval-${score.id}`).style.width = `${pct}%`;
        document.getElementById(`eval-${score.id}-value`).textContent = `${pct}%`;
    });
    
    // 요약
    document.getElementById('eval-summary-text').textContent = evaluation.summary || '';
    
    // 강점
    const strengthsList = document.getElementById('eval-strengths');
    strengthsList.innerHTML = (evaluation.strengths || []).map(s => `<li>${escapeHtml(s)}</li>`).join('');
    
    // 제안
    const suggestionsList = document.getElementById('eval-suggestions');
    suggestionsList.innerHTML = (evaluation.suggestions || []).map(s => `<li>${escapeHtml(s)}</li>`).join('');
}

function getSceneTypeName(type) {
    const types = {
        'dialogue': '대화',
        'opening': '오프닝',
        'talk': '본격 토크',
        'highlight': '하이라이트',
        'closing': '마무리',
        'action': '액션',
        'transition': '전환'
    };
    return types[type] || type || '대화';
}

function getScoreClass(score) {
    if (score >= 0.8) return 'high';
    if (score >= 0.6) return 'medium';
    return '';
}

// 탭 전환 시 데이터 로드 확장
const originalSwitchTab = switchTab;
switchTab = function(tabName) {
    originalSwitchTab(tabName);
    
    if (tabName === 'scripts') {
        loadAllScenes();
    } else if (tabName === 'synopsis') {
        loadSynopsis();
    }
};

// ==================== 시놉시스 Functions ====================

async function loadSynopsis() {
    if (!state.currentProject) return;
    
    const container = document.getElementById('synopsis-container');
    container.innerHTML = '<div class="loading-indicator">시놉시스 로딩 중...</div>';
    
    try {
        const response = await fetch(`/api/projects/${state.currentProject.id}/synopsis`);
        
        if (response.ok) {
            const synopsis = await response.json();
            state.synopsis = synopsis;
            renderSynopsis(synopsis);
        } else if (response.status === 404) {
            // 시놉시스가 없는 경우
            state.synopsis = null;
            renderEmptySynopsis();
        } else {
            throw new Error('시놉시스를 불러오는 데 실패했습니다');
        }
    } catch (error) {
        console.error('Failed to load synopsis:', error);
        container.innerHTML = `
            <div class="empty-synopsis">
                <div class="empty-synopsis-icon">❌</div>
                <h4>시놉시스를 불러올 수 없습니다</h4>
                <p>${error.message}</p>
            </div>
        `;
    }
}

function renderEmptySynopsis() {
    const container = document.getElementById('synopsis-container');
    container.innerHTML = `
        <div class="empty-synopsis">
            <div class="empty-synopsis-icon">📋</div>
            <h4>시놉시스가 없습니다</h4>
            <p>이 프로젝트의 시놉시스를 작성해보세요</p>
            <button class="btn-primary" onclick="showNewSynopsisModal()">
                + 시놉시스 작성
            </button>
        </div>
    `;
}

function renderSynopsis(synopsis) {
    const container = document.getElementById('synopsis-container');
    
    // 마크다운 형태로 표시
    const contentHtml = synopsis.content ? 
        formatSynopsisContent(synopsis.content) : 
        '<p class="no-content">내용이 없습니다</p>';
    
    container.innerHTML = `
        <div class="synopsis-header">
            <div class="synopsis-title-area">
                <h2>${escapeHtml(synopsis.title || '제목 없음')}</h2>
                ${synopsis.version ? `<span class="synopsis-version">v${synopsis.version}</span>` : ''}
            </div>
            <div class="synopsis-actions">
                <button class="btn-secondary" onclick="editSynopsis()">
                    ✏️ 편집
                </button>
                <button class="btn-secondary" onclick="generateSynopsisFromAI()">
                    🤖 AI 생성
                </button>
                <button class="btn-secondary" onclick="exportSynopsis()">
                    📥 내보내기
                </button>
            </div>
        </div>
        
        <div class="synopsis-meta">
            ${synopsis.genre ? `<span class="meta-tag">🎭 ${escapeHtml(synopsis.genre)}</span>` : ''}
            ${synopsis.target_audience ? `<span class="meta-tag">👥 ${escapeHtml(synopsis.target_audience)}</span>` : ''}
            ${synopsis.estimated_length ? `<span class="meta-tag">📖 ${escapeHtml(synopsis.estimated_length)}</span>` : ''}
            ${synopsis.updated_at ? `<span class="meta-date">최종 수정: ${formatDate(synopsis.updated_at)}</span>` : ''}
        </div>
        
        ${synopsis.logline ? `
            <div class="synopsis-section logline-section">
                <h3>📍 로그라인</h3>
                <p class="logline-text">${escapeHtml(synopsis.logline)}</p>
            </div>
        ` : ''}
        
        ${synopsis.premise ? `
            <div class="synopsis-section">
                <h3>💡 전제 (Premise)</h3>
                <p>${escapeHtml(synopsis.premise)}</p>
            </div>
        ` : ''}
        
        ${synopsis.theme ? `
            <div class="synopsis-section">
                <h3>🎯 주제 (Theme)</h3>
                <p>${escapeHtml(synopsis.theme)}</p>
            </div>
        ` : ''}
        
        <div class="synopsis-section main-content-section">
            <h3>📝 시놉시스 본문</h3>
            <div class="synopsis-content">
                ${contentHtml}
            </div>
        </div>
        
        ${synopsis.plot_points && synopsis.plot_points.length > 0 ? `
            <div class="synopsis-section">
                <h3>📊 주요 플롯 포인트</h3>
                <div class="plot-points">
                    ${synopsis.plot_points.map((point, idx) => `
                        <div class="plot-point">
                            <span class="plot-number">${idx + 1}</span>
                            <div class="plot-content">
                                <strong>${escapeHtml(point.title || `포인트 ${idx + 1}`)}</strong>
                                <p>${escapeHtml(point.description || '')}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
        
        ${synopsis.character_arcs && synopsis.character_arcs.length > 0 ? `
            <div class="synopsis-section">
                <h3>🎭 캐릭터 아크</h3>
                <div class="character-arcs">
                    ${synopsis.character_arcs.map(arc => `
                        <div class="character-arc-card">
                            <div class="arc-header">
                                <span class="arc-name">${escapeHtml(arc.character_name || '캐릭터')}</span>
                            </div>
                            <div class="arc-journey">
                                <div class="arc-point start">
                                    <span class="arc-label">시작</span>
                                    <p>${escapeHtml(arc.start_state || '')}</p>
                                </div>
                                <div class="arc-arrow">→</div>
                                <div class="arc-point end">
                                    <span class="arc-label">끝</span>
                                    <p>${escapeHtml(arc.end_state || '')}</p>
                                </div>
                            </div>
                            ${arc.key_moment ? `<p class="arc-moment">핵심 순간: ${escapeHtml(arc.key_moment)}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
        
        ${synopsis.notes ? `
            <div class="synopsis-section notes-section">
                <h3>📌 참고 사항</h3>
                <p>${escapeHtml(synopsis.notes)}</p>
            </div>
        ` : ''}
    `;
}

function formatSynopsisContent(content) {
    // 간단한 마크다운 → HTML 변환
    let html = escapeHtml(content);
    
    // 줄바꿈 처리
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    
    // **bold** 처리
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // *italic* 처리
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    return `<p>${html}</p>`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showNewSynopsisModal() {
    document.getElementById('modal-new-synopsis').classList.add('active');
    
    // 프로젝트 정보 기반 기본값 설정
    if (state.currentProject) {
        document.getElementById('synopsis-title').value = state.currentProject.title + ' 시놉시스';
    }
}

async function createSynopsis() {
    const title = document.getElementById('synopsis-title').value.trim();
    const logline = document.getElementById('synopsis-logline').value.trim();
    const premise = document.getElementById('synopsis-premise').value.trim();
    const theme = document.getElementById('synopsis-theme').value.trim();
    const genre = document.getElementById('synopsis-genre').value.trim();
    const content = document.getElementById('synopsis-content').value.trim();
    
    if (!title) {
        showToast('시놉시스 제목을 입력하세요', 'error');
        return;
    }
    
    try {
        const result = await api(`/api/projects/${state.currentProject.id}/synopsis`, {
            method: 'POST',
            body: JSON.stringify({
                title,
                logline,
                premise,
                theme,
                genre,
                content,
                version: 1
            })
        });
        
        showToast('시놉시스가 생성되었습니다');
        closeModal('modal-new-synopsis');
        
        // 폼 초기화
        document.getElementById('synopsis-title').value = '';
        document.getElementById('synopsis-logline').value = '';
        document.getElementById('synopsis-premise').value = '';
        document.getElementById('synopsis-theme').value = '';
        document.getElementById('synopsis-genre').value = '';
        document.getElementById('synopsis-content').value = '';
        
        await loadSynopsis();
    } catch (error) {
        console.error('Failed to create synopsis:', error);
    }
}

function editSynopsis() {
    if (!state.synopsis) return;
    
    // 편집 모달 열기 (기존 데이터로 채우기)
    document.getElementById('synopsis-title').value = state.synopsis.title || '';
    document.getElementById('synopsis-logline').value = state.synopsis.logline || '';
    document.getElementById('synopsis-premise').value = state.synopsis.premise || '';
    document.getElementById('synopsis-theme').value = state.synopsis.theme || '';
    document.getElementById('synopsis-genre').value = state.synopsis.genre || '';
    document.getElementById('synopsis-content').value = state.synopsis.content || '';
    
    // 편집 모드 플래그 설정
    document.getElementById('modal-new-synopsis').dataset.editMode = 'true';
    document.getElementById('modal-new-synopsis').classList.add('active');
}

async function saveSynopsis() {
    const modal = document.getElementById('modal-new-synopsis');
    const isEditMode = modal.dataset.editMode === 'true';
    
    const title = document.getElementById('synopsis-title').value.trim();
    const logline = document.getElementById('synopsis-logline').value.trim();
    const premise = document.getElementById('synopsis-premise').value.trim();
    const theme = document.getElementById('synopsis-theme').value.trim();
    const genre = document.getElementById('synopsis-genre').value.trim();
    const content = document.getElementById('synopsis-content').value.trim();
    
    if (!title) {
        showToast('시놉시스 제목을 입력하세요', 'error');
        return;
    }
    
    try {
        const method = isEditMode ? 'PUT' : 'POST';
        const result = await api(`/api/projects/${state.currentProject.id}/synopsis`, {
            method: method,
            body: JSON.stringify({
                title,
                logline,
                premise,
                theme,
                genre,
                content,
                version: isEditMode ? (state.synopsis?.version || 1) + 1 : 1
            })
        });
        
        showToast(isEditMode ? '시놉시스가 수정되었습니다' : '시놉시스가 생성되었습니다');
        closeModal('modal-new-synopsis');
        modal.dataset.editMode = 'false';
        
        await loadSynopsis();
    } catch (error) {
        console.error('Failed to save synopsis:', error);
    }
}

async function generateSynopsisFromAI() {
    if (!state.currentProject) return;
    
    const confirmed = confirm(
        'AI가 프로젝트의 캐릭터와 에피소드 정보를 기반으로 시놉시스를 생성합니다.\n' +
        '기존 시놉시스가 있다면 덮어쓰게 됩니다.\n\n계속하시겠습니까?'
    );
    
    if (!confirmed) return;
    
    const container = document.getElementById('synopsis-container');
    container.innerHTML = `
        <div class="loading-synopsis">
            <div class="loading-spinner"></div>
            <h4>AI가 시놉시스를 생성 중입니다...</h4>
            <p>캐릭터와 에피소드 정보를 분석하고 있습니다</p>
        </div>
    `;
    
    try {
        const result = await api(`/api/generate/synopsis`, {
            method: 'POST',
            body: JSON.stringify({
                project_id: state.currentProject.id
            })
        });
        
        showToast('AI 시놉시스가 생성되었습니다!');
        await loadSynopsis();
    } catch (error) {
        console.error('Failed to generate synopsis:', error);
        await loadSynopsis(); // 기존 상태로 복구
    }
}

function exportSynopsis() {
    if (!state.synopsis) {
        showToast('내보낼 시놉시스가 없습니다', 'error');
        return;
    }
    
    // 마크다운 형식으로 내보내기
    let markdown = `# ${state.synopsis.title || '시놉시스'}\n\n`;
    
    if (state.synopsis.logline) {
        markdown += `## 로그라인\n${state.synopsis.logline}\n\n`;
    }
    
    if (state.synopsis.premise) {
        markdown += `## 전제 (Premise)\n${state.synopsis.premise}\n\n`;
    }
    
    if (state.synopsis.theme) {
        markdown += `## 주제 (Theme)\n${state.synopsis.theme}\n\n`;
    }
    
    if (state.synopsis.content) {
        markdown += `## 시놉시스 본문\n${state.synopsis.content}\n\n`;
    }
    
    if (state.synopsis.notes) {
        markdown += `## 참고 사항\n${state.synopsis.notes}\n\n`;
    }
    
    // 파일 다운로드
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${state.synopsis.title || 'synopsis'}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('시놉시스가 마크다운 파일로 저장되었습니다');
}

