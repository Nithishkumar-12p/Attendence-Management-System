const SHIFT_API = 'http://localhost:5000/api/shifts';
const EMP_API = 'http://localhost:5000/api/employees';

let allShifts = [];
let allEmployees = [];
let selectedEmployeeIds = new Set();
let currentAssignmentShiftId = null;

// ─── Initialize ──────────────────────────────────────────────────────────────
async function init() {
    await fetchGlobalSettings();
    await fetchShifts();
    await fetchAllEmployees();
    setupEventListeners();
}

async function fetchGlobalSettings() {
    try {
        const res = await fetch('http://localhost:5000/api/settings/');
        const settings = await res.json();
        const companyName = settings.company_name || 'INDUSTRIAL ATTENDANCE';
        updateSidebarBanner(companyName);
    } catch (err) {
        console.error('Error fetching global settings:', err);
    }
}

function updateSidebarBanner(name) {
    const sidebarTitle = document.getElementById('sidebarCompanyName');
    if (sidebarTitle) sidebarTitle.textContent = name;
}

// ─── Fetch Data ──────────────────────────────────────────────────────────────
async function fetchShifts() {
    try {
        const res = await fetch(`${SHIFT_API}/`);
        allShifts = await res.json();
        renderShiftsGrid();
        updatePreviewStrip();
    } catch (err) {
        console.error('Error fetching shifts:', err);
        showToast('Failed to load shifts', 'error');
    }
}

async function fetchAllEmployees() {
    try {
        const res = await fetch(`${EMP_API}/`);
        allEmployees = await res.json();
    } catch (err) {
        console.error('Error fetching employees:', err);
    }
}

// ─── Render UI ───────────────────────────────────────────────────────────────
function renderShiftsGrid() {
    const grid = document.getElementById('shiftsGrid');
    if (!grid) return;

    if (allShifts.length === 0) {
        grid.innerHTML = '<p style="text-align:center; padding:2rem; color:var(--text-dim); width:100%;">No shifts found. Create one to get started.</p>';
        return;
    }

    grid.innerHTML = allShifts.map(shift => `
        <div class="shift-card">
            <div class="shift-card-header">
                <div class="shift-name">${shift.name}</div>
                <div class="shift-time-badge">
                    <i class="fa-solid fa-clock"></i> ${formatTime(shift.start_time)} - ${formatTime(shift.end_time)}
                </div>
            </div>
            <div class="shift-details">
                <div class="detail-item">
                    <span class="detail-label">Members</span>
                    <span class="detail-value">${shift.member_count} active</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Working Hours</span>
                    <span class="detail-value">${shift.working_hours} hrs</span>
                </div>
            </div>
            <div class="shift-actions">
                <button class="btn-save" style="padding:0.4rem 0.8rem; font-size:0.8rem; flex:1;" onclick="manageMembers(${shift.id})">
                    <i class="fa-solid fa-users"></i> Assign
                </button>
                <div style="display:flex; gap:0.4rem;">
                    <button class="btn-icon" onclick="editShift(${shift.id})" title="Edit Timings">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn-icon delete" onclick="deleteShift(${shift.id})" title="Delete Shift">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function updatePreviewStrip() {
    if (allShifts.length > 0) {
        const avgGrace = Math.round(allShifts.reduce((acc, s) => acc + s.grace_period, 0) / allShifts.length);
        const shiftTimes = `${formatTime(allShifts[0].start_time)} - ${formatTime(allShifts[0].end_time)}`;
        
        document.getElementById('prev_shift').textContent = shiftTimes;
        document.getElementById('prev_total_shifts').textContent = allShifts.length;
        document.getElementById('prev_grace').textContent = `${avgGrace} mins`;
    }
}

function formatTime(t) {
    if (!t) return '--:--';
    // Handle "HH:MM:SS" or "HH:MM"
    return t.substring(0, 5);
}

// ─── Shift CRUD ──────────────────────────────────────────────────────────────
window.showShiftModal = (shift = null) => {
    const modal = document.getElementById('shiftModal');
    const title = document.getElementById('shiftModalTitle');
    const form = document.getElementById('shiftForm');
    
    if (shift) {
        title.textContent = 'Edit Shift';
        form.shift_id.value = shift.id;
        form.shift_name.value = shift.name;
        form.s_start_time.value = formatTime(shift.start_time);
        form.s_end_time.value = formatTime(shift.end_time);
        form.s_working_hours.value = shift.working_hours;
        form.s_grace_period.value = shift.grace_period;
    } else {
        title.textContent = 'Add New Shift';
        form.reset();
        form.shift_id.value = '';
    }
    
    // Auto-calculate hours immediately on open
    window.autoCalculateHours();
    
    modal.classList.add('show');
};

window.autoCalculateHours = () => {
    const startVal = document.getElementById('s_start_time').value;
    const endVal = document.getElementById('s_end_time').value;
    const hoursInput = document.getElementById('s_working_hours');
    
    if (startVal && endVal) {
        const startParts = startVal.split(':');
        const endParts = endVal.split(':');
        
        if (startParts.length >= 2 && endParts.length >= 2) {
            const h1 = parseInt(startParts[0]);
            const m1 = parseInt(startParts[1]);
            const h2 = parseInt(endParts[0]);
            const m2 = parseInt(endParts[1]);
            
            if (!isNaN(h1) && !isNaN(m1) && !isNaN(h2) && !isNaN(m2)) {
                let startTime = h1 + (m1 / 60);
                let endTime = h2 + (m2 / 60);
                
                let diff = endTime - startTime;
                if (diff < 0) diff += 24; // Handle overnight shift
                
                hoursInput.value = diff.toFixed(1);
            }
        }
    }
};

window.hideShiftModal = () => {
    document.getElementById('shiftModal').classList.remove('show');
};

async function handleShiftSubmit(e) {
    e.preventDefault();
    const shiftId = document.getElementById('shift_id').value;
    
    const payload = {
        name: document.getElementById('shift_name').value,
        start_time: document.getElementById('s_start_time').value,
        end_time: document.getElementById('s_end_time').value,
        working_hours: parseFloat(document.getElementById('s_working_hours').value),
        grace_period: parseInt(document.getElementById('s_grace_period').value)
    };

    try {
        const method = shiftId ? 'PUT' : 'POST';
        const url = shiftId ? `${SHIFT_API}/${shiftId}` : `${SHIFT_API}/`;
        
        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (data.success) {
            showToast(shiftId ? 'Shift updated!' : 'Shift created!');
            hideShiftModal();
            fetchShifts();
        } else {
            showToast(data.error || 'Failed to save shift', 'error');
        }
    } catch (err) {
        showToast('Network error', 'error');
    }
}

window.editShift = (id) => {
    const shift = allShifts.find(s => s.id === id);
    if (shift) showShiftModal(shift);
};

window.deleteShift = async (id) => {
    if (!confirm('Are you sure you want to delete this shift?')) return;
    
    try {
        const res = await fetch(`${SHIFT_API}/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            showToast('Shift deleted');
            fetchShifts();
        } else {
            showToast(data.error || 'Cannot delete shift', 'error');
        }
    } catch (err) {
        showToast('Error deleting shift', 'error');
    }
};

// ─── Member Assignment logic ────────────────────────────────────────────────
window.manageMembers = (shiftId) => {
    currentAssignmentShiftId = shiftId;
    const shift = allShifts.find(s => s.id === shiftId);
    document.getElementById('memberShiftName').textContent = `Assigning to: ${shift.name}`;
    
    // Reset selection and find members already in this shift
    selectedEmployeeIds.clear();
    allEmployees.forEach(emp => {
        // emp is an object from the API: { employee_id, name, shift_id, ... }
        if (emp.shift_id === shiftId) {
            selectedEmployeeIds.add(emp.employee_id);
        }
    });

    renderMemberList();
    document.getElementById('membersModal').classList.add('show');
};

function renderMemberList(filter = '') {
    const list = document.getElementById('membersList');
    const resultsCountEl = document.getElementById('resultsCount');
    const clearBtn = document.getElementById('clearMemberSearch');

    // Show/hide clear button
    if (clearBtn) clearBtn.style.display = filter ? 'flex' : 'none';

    const filtered = allEmployees.filter(emp => 
        emp.name.toLowerCase().includes(filter.toLowerCase()) || 
        emp.employee_id.toString().includes(filter)
    );

    if (resultsCountEl) {
        resultsCountEl.textContent = filter 
            ? `Found ${filtered.length} member${filtered.length !== 1 ? 's' : ''}` 
            : `Showing all ${allEmployees.length} members`;
    }

    if (filtered.length === 0) {
        list.innerHTML = `
            <div style="text-align:center; padding:3rem; color:var(--text-dim);">
                <i class="fa-solid fa-user-slash" style="font-size:2rem; margin-bottom:1rem; opacity:0.3;"></i>
                <p>No members found matching "${filter}"</p>
            </div>
        `;
        return;
    }

    list.innerHTML = filtered.map(emp => {
        const isSelected = selectedEmployeeIds.has(emp.employee_id);
        const initials = emp.name.split(' ').map(n => n[0]).join('').substring(0, 2);
        
        // Show current shift name if not this one
        let currentShiftHtml = '';
        if (emp.shift_id && emp.shift_id !== currentAssignmentShiftId) {
            const s = allShifts.find(sh => sh.id === emp.shift_id);
            currentShiftHtml = s ? `<span class="member-current-shift">${s.name}</span>` : '';
        }

        return `
            <div class="member-row ${isSelected ? 'selected' : ''}" onclick="toggleMemberSelection(${emp.employee_id})">
                <div class="member-avatar">${initials}</div>
                <div class="member-info">
                    <div class="member-name">
                        ${emp.name}
                        ${currentShiftHtml}
                    </div>
                    <div class="member-meta">
                        <span class="designation-badge">${emp.designation || 'Worker'}</span>
                    </div>
                </div>
                <div class="checkbox-custom">
                    <i class="fa-solid fa-check"></i>
                </div>
            </div>
        `;
    }).join('');
}

window.toggleMemberSelection = (id) => {
    if (selectedEmployeeIds.has(id)) {
        selectedEmployeeIds.delete(id);
    } else {
        selectedEmployeeIds.add(id);
    }
    renderMemberList(document.getElementById('memberSearch').value);
};

window.hideMembersModal = () => {
    document.getElementById('membersModal').classList.remove('show');
};

async function saveAssignment() {
    const btn = document.getElementById('saveAssignmentBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

    try {
        const res = await fetch(`${SHIFT_API}/assign`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                shift_id: currentAssignmentShiftId,
                employee_ids: Array.from(selectedEmployeeIds)
            })
        });
        
        const data = await res.json();
        if (data.success) {
            showToast('Assignment updated successfully!');
            hideMembersModal();
            fetchShifts();
            fetchAllEmployees(); // Update local list for indices
        } else {
            showToast(data.error || 'Failed to update assignment', 'error');
        }
    } catch (err) {
        showToast('Network error', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Confirm Assignment';
    }
}

// ─── Utilities ───────────────────────────────────────────────────────────────
function setupEventListeners() {
    document.getElementById('shiftForm').addEventListener('submit', handleShiftSubmit);
    document.getElementById('saveAssignmentBtn').addEventListener('click', saveAssignment);
    
    const searchInput = document.getElementById('memberSearch');
    const searchBtn = document.getElementById('memberSearchBtn');
    const clearBtn = document.getElementById('clearMemberSearch');

    // Real-time search
    searchInput.addEventListener('input', (e) => renderMemberList(e.target.value));
    
    // Explicit search button
    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            renderMemberList(searchInput.value);
            // Visual feedback
            searchBtn.classList.add('btn-pulse');
            setTimeout(() => searchBtn.classList.remove('btn-pulse'), 500);
        });
    }

    // Clear search
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            renderMemberList('');
            searchInput.focus();
        });
    }

    // Handle Enter key in search
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            renderMemberList(searchInput.value);
        }
    });
    
    // Global Save Button
    document.getElementById('saveBtn').addEventListener('click', () => {
        showToast('Shift settings saved');
    });

    // Global Reset Button
    document.getElementById('resetBtn').addEventListener('click', async () => {
        if (confirm('Reset settings to defaults?')) {
            showToast('Settings reset');
        }
    });

    // Auto-calculate hours listeners
    document.getElementById('s_start_time').addEventListener('input', window.autoCalculateHours);
    document.getElementById('s_end_time').addEventListener('input', window.autoCalculateHours);
}

function showToast(msg, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = document.getElementById('toastIcon');
    const text = document.getElementById('toastText');

    toast.className = `toast ${type}`;
    icon.className = `toast-icon fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}`;
    text.textContent = msg;

    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3500);
}

// ─── Start ───────────────────────────────────────────────────────────────────
init();
