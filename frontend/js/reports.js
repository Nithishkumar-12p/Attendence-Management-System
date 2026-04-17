        const today = new Date().toISOString().split('T')[0];
        let currentTab = 'daily';
        let cachedData = { daily: [], range: [], workers: [], payroll: [] };

        document.getElementById('filterFrom').value = today;
        document.getElementById('filterTo').value = today;

        // ─── Tab Switching ─────────────────────────────────────────────────
        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            document.getElementById('tab-' + tab).classList.add('active');
            document.getElementById('pane-' + tab).classList.add('active');

            // Show date filter only for relevant tabs
            const showFilter = ['daily', 'range'].includes(tab);
            document.getElementById('dateFilterRow').style.display = showFilter ? 'flex' : 'none';

            // Refresh data automatically on tab switch
            if (tab === 'daily') loadDaily();
            if (tab === 'range') loadRange();
            if (tab === 'workers') loadWorkers();
            if (tab === 'payroll') loadPayroll();
        }

        // ─── Apply Date Filter ─────────────────────────────────────────────
        function applyDateFilter() {
            if (currentTab === 'daily') loadDaily();
            if (currentTab === 'range') loadRange();
        }

        // ─── DAILY ────────────────────────────────────────────────────────
        async function loadDaily() {
            const date = document.getElementById('filterFrom').value;
            document.getElementById('dailyBody').innerHTML = '<tr class="loading-row"><td colspan="8">Loading...</td></tr>';
            try {
                const res = await fetch(`http://localhost:5000/api/attendance/list/${date}`);
                const data = await res.json();
                cachedData.daily = data;

                const present = data.filter(r => r.status === 'P').length;
                const absent  = data.filter(r => r.status === 'A').length;
                const late    = data.filter(r => r.is_late).length;

                if (!data.length) {
                    document.getElementById('dailyBody').innerHTML = `<tr class="loading-row"><td colspan="8">No attendance records found for ${date}.</td></tr>`;
                    return;
                }
                document.getElementById('dailyBody').innerHTML = data.map(r => `
                    <tr>
                        <td style="color:var(--text-dim)">${r.employee_id}</td>
                        <td style="font-weight:600">${r.name}</td>
                        <td>${statusBadge(r.status)}</td>
                        <td>${r.in_time || '-'}</td>
                        <td>${r.out_time || '-'}</td>
                        <td>${r.is_late ? '<span class="badge-error">LATE</span>' : '<span class="badge-p">ON TIME</span>'}</td>
                        <td style="text-align:center">${r.tools_count || 0}</td>
                        <td style="color:var(--text-dim); font-style: italic;">${r.remarks || '-'}</td>
                    </tr>
                `).join('');
                applySearchFilter();
            } catch(e) {
                document.getElementById('dailyBody').innerHTML = `<tr class="loading-row"><td colspan="8">Error loading data. Is the server running?</td></tr>`;
            }
        }

        // ─── RANGE ────────────────────────────────────────────────────────
        async function loadRange() {
            const s = document.getElementById('filterFrom').value;
            const e = document.getElementById('filterTo').value;
            document.getElementById('rangeBody').innerHTML = '<tr class="loading-row"><td colspan="8">Loading...</td></tr>';
            try {
                const res = await fetch(`http://localhost:5000/api/attendance/range?start_date=${s}&end_date=${e}`);
                const data = await res.json();
                cachedData.range = data;

                if (!data.length) {
                    document.getElementById('rangeBody').innerHTML = `<tr class="loading-row"><td colspan="8">No records found for this date range.</td></tr>`;
                    return;
                }
                document.getElementById('rangeBody').innerHTML = data.map(r => `
                    <tr>
                        <td style="color:var(--text-dim)">${r.date}</td>
                        <td style="color:var(--text-dim)">${r.employee_id}</td>
                        <td style="font-weight:600">${r.name}</td>
                        <td>${statusBadge(r.status)}</td>
                        <td>${r.in_time || '-'}</td>
                        <td>${r.out_time || '-'}</td>
                        <td style="text-align:center">${r.tools_count || 0}</td>
                        <td style="color:var(--text-dim); font-style:italic;">${r.remarks || '-'}</td>
                    </tr>
                `).join('');
                applySearchFilter();
            } catch(e) {
                document.getElementById('rangeBody').innerHTML = `<tr class="loading-row"><td colspan="8">Error loading data. Make sure start_date &le; end_date.</td></tr>`;
            }
        }

        // ─── WORKERS ──────────────────────────────────────────────────────
        async function loadWorkers() {
            try {
                const res = await fetch('http://localhost:5000/api/employees/');
                const data = await res.json();
                cachedData.workers = data;

                document.getElementById('workerBody').innerHTML = data.map(r => `
                    <tr>
                        <td style="color:var(--text-dim)">${r.employee_id}</td>
                        <td style="font-weight:600">${r.name}</td>
                        <td><span class="badge-cl">${r.designation || 'N/A'}</span></td>
                        <td style="color:var(--primary); font-weight:600;">₹${Number(r.basic_salary).toLocaleString()}</td>
                        <td>${r.phone_number || '-'}</td>
                        <td>${r.contract_start_date || '-'}</td>
                        <td>${r.contract_end_date || '-'}</td>
                        <td style="text-align:center">${r.working_hours_per_day || 8}</td>
                        <td><span class="${r.is_active ? 'badge-p' : 'badge-error'}">${r.is_active ? 'ACTIVE' : 'EXPIRED'}</span></td>
                    </tr>
                `).join('');
                applySearchFilter();
            } catch(e) {
                document.getElementById('workerBody').innerHTML = `<tr class="loading-row"><td colspan="9">Error loading worker data.</td></tr>`;
            }
        }

        // ─── PAYROLL ──────────────────────────────────────────────────────
        async function loadPayroll() {
            const m = document.getElementById('payMonth').value;
            const y = document.getElementById('payYear').value;
            document.getElementById('payrollBody').innerHTML = '<tr class="loading-row"><td colspan="8">Loading...</td></tr>';
            try {
                const res = await fetch(`http://localhost:5000/api/salary/report/${m}/${y}`);
                const data = await res.json();
                cachedData.payroll = data;

                const totalPay = data.reduce((acc, r) => acc + (r.final_salary||0), 0);
                const totalDed = data.reduce((acc, r) => acc + (r.deductions||0), 0);
                const monthName = document.getElementById('payMonth').options[document.getElementById('payMonth').selectedIndex].text;

                if (!data.length) {
                    document.getElementById('payrollBody').innerHTML = `<tr class="loading-row"><td colspan="8">No salary data. Go to <a href="salary.html" style="color:var(--primary)">Salary page</a> to generate.</td></tr>`;
                    return;
                }
                document.getElementById('payrollBody').innerHTML = data.map(r => `
                    <tr>
                        <td style="color:var(--text-dim)">${r.employee_id}</td>
                        <td style="font-weight:600">${r.name}</td>
                        <td><span class="badge-cl">${r.designation || '-'}</span></td>
                        <td>₹${Number(r.basic_salary).toLocaleString()}</td>
                        <td style="color:var(--success); font-weight:600;">${r.present_days}</td>
                        <td style="color:var(--danger);">${r.absent_days}</td>
                        <td style="font-weight:700; color:var(--success);">₹${Number(r.final_salary).toLocaleString()}</td>
                    </tr>
                `).join('');
                applySearchFilter();
            } catch(e) {
                document.getElementById('payrollBody').innerHTML = `<tr class="loading-row"><td colspan="8">Error loading payroll data.</td></tr>`;
            }
        }

        // ─── EXPORTS ──────────────────────────────────────────────────────
        function exportCurrentPDF() {
            const from = document.getElementById('filterFrom').value;
            const to   = document.getElementById('filterTo').value;
            const m    = document.getElementById('payMonth').value;
            const y    = document.getElementById('payYear').value;

            if (currentTab === 'daily')   window.location.href = `http://localhost:5000/api/reports/pdf/daily/${from}`;
            if (currentTab === 'range')   window.location.href = `http://localhost:5000/api/reports/pdf/range?start_date=${from}&end_date=${to}`;
            if (currentTab === 'workers') window.location.href = `http://localhost:5000/api/reports/pdf/employees`;
            if (currentTab === 'payroll') window.location.href = `http://localhost:5000/api/reports/pdf/salary/${m}/${y}`;
        }



        // ─── Helpers ──────────────────────────────────────────────────────
        function statusBadge(s) {
            const map = { P:'badge-p', A:'badge-a', CL:'badge-cl', SL:'badge-sl', HD:'badge-hd' };
            const label = { P:'PRESENT', A:'ABSENT', CL:'CASUAL LEAVE', SL:'SICK LEAVE', HD:'HALF DAY' };
            return `<span class="${map[s]||'badge-a'}">${label[s]||s}</span>`;
        }

        // ─── Filter Search ────────────────────────────────────────────────
        function applySearchFilter() {
            const searchInput = document.getElementById('reportSearch');
            const clearBtn = document.getElementById('btnClearSearch');
            const term = searchInput.value.toLowerCase();
            
            // Toggle clear button
            if (clearBtn) {
                clearBtn.style.display = term ? 'block' : 'none';
            }

            const activePane = document.querySelector('.tab-pane.active');
            if (!activePane) return;
            
            const rows = activePane.querySelectorAll('tbody tr:not(.loading-row)');
            let visibleCount = 0;
            
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                const isMatch = text.includes(term);
                row.style.display = isMatch ? '' : 'none';
                if (isMatch) visibleCount++;
            });
        }

        // ─── Event Listeners ──────────────────────────────────────────────
        document.getElementById('reportSearch').addEventListener('input', applySearchFilter);
        
        // Search on Enter key
        document.getElementById('reportSearch').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                applySearchFilter();
            }
        });

        // Search Button click
        document.getElementById('btnSearch').addEventListener('click', applySearchFilter);

        // Clear Search
        document.getElementById('btnClearSearch').addEventListener('click', () => {
            document.getElementById('reportSearch').value = '';
            applySearchFilter();
            document.getElementById('reportSearch').focus();
        });

        // ─── Init ─────────────────────────────────────────────────────────
        loadDaily();
        loadWorkers();
