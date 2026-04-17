        let allEmployees = [];
        let attendanceData = {};

        const today = new Date().toISOString().split('T')[0];
        document.getElementById('displayDate').innerText = today;
        document.getElementById('datePicker').value = today;

        let allShifts = [];

        // Initialize Page
        async function init() {
            await fetchEmployees();
            await fetchShifts();
            await fetchExistingAttendance(today);
            renderTable();
        }

        async function fetchShifts() {
            try {
                const res = await fetch('http://localhost:5000/api/shifts/');
                allShifts = await res.json();
            } catch (err) {
                console.error('Error fetching shifts:', err);
            }
        }

        async function fetchEmployees() {
            const res = await fetch('http://localhost:5000/api/employees/');
            allEmployees = await res.json();
        }

        async function fetchExistingAttendance(date) {
            const res = await fetch(`http://localhost:5000/api/attendance/list/${date}`);
            const data = await res.json();
            // Map into dictionary for easy access
            attendanceData = {};
            data.forEach(item => {
                attendanceData[item.employee_id] = item;
            });
        }

        function renderTable(filterText = '') {
            const tbody = document.getElementById('attendanceBody');
            tbody.innerHTML = '';

            const filtered = allEmployees.filter(emp => 
                String(emp.name).toLowerCase().includes(filterText.toLowerCase()) || 
                String(emp.employee_id).toLowerCase().includes(filterText.toLowerCase())
            );

            filtered.forEach(emp => {
                const shift = allShifts.find(s => s.id === emp.shift_id) || { start_time: '09:00:00', end_time: '18:00:00', name: 'General' };
                const defaultIn = shift.start_time.substring(0, 5);
                const defaultOut = shift.end_time.substring(0, 5);

                const existing = attendanceData[emp.employee_id] || { 
                    status: 'A', 
                    in_time: '-', 
                    out_time: '-' 
                };
                
                const row = document.createElement('tr');
                row.className = 'attendance-row';
                row.innerHTML = `
                    <td>${emp.employee_id}</td>
                    <td>
                        <div style="font-weight:600;">${emp.name}</div>
                        <div style="font-size:0.7rem; color:var(--text-dim);">Shift: ${shift.name}</div>
                    </td>
                    <td>
                        <input type="time" class="time-input" value="${existing.in_time !== '-' && existing.in_time !== '00:00' ? existing.in_time : defaultIn}" 
                               ${existing.status !== 'P' && existing.status !== 'HD' ? 'disabled' : ''} 
                               onchange="updateField('${emp.employee_id}', 'in_time', this.value)">
                    </td>
                    <td>
                        <input type="time" class="time-input" value="${existing.out_time !== '-' && existing.out_time !== '00:00' ? existing.out_time : defaultOut}" 
                               ${existing.status !== 'P' && existing.status !== 'HD' ? 'disabled' : ''} 
                               onchange="updateField('${emp.employee_id}', 'out_time', this.value)">
                    </td>
                    <td>
                        <input type="number" class="time-input" placeholder="0" value="${existing.tools_count || 0}" 
                               onchange="updateField('${emp.employee_id}', 'tools_count', parseInt(this.value) || 0)">
                    </td>
                    <td>
                        <input type="text" placeholder="e.g. Drill, Hammer" value="${existing.tools_details || ''}" 
                               onchange="updateField('${emp.employee_id}', 'tools_details', this.value)">
                    </td>
                    <td>
                        <input type="text" placeholder="Type of work..." value="${existing.remarks || emp.designation || ''}" 
                               onchange="updateField('${emp.employee_id}', 'remarks', this.value)">
                    </td>
                    <td>
                        <select class="status-select status-${existing.status || 'A'}" onchange="handleStatusChange(this, '${emp.employee_id}')">
                            <option value="P" ${existing.status === 'P' ? 'selected' : ''}>Present</option>
                            <option value="A" ${existing.status === 'A' ? 'selected' : ''}>Absent</option>
                            <option value="CL" ${existing.status === 'CL' ? 'selected' : ''}>Casual Leave</option>
                            <option value="SL" ${existing.status === 'SL' ? 'selected' : ''}>Sick Leave</option>
                            <option value="HD" ${existing.status === 'HD' ? 'selected' : ''}>Half Day</option>
                        </select>
                    </td>
                `;
                tbody.appendChild(row);

                // Ensure internal data has proper defaults immediately
                if (existing.in_time === '-' || !existing.in_time) existing.in_time = defaultIn;
                if (existing.out_time === '-' || !existing.out_time) existing.out_time = defaultOut;

                // Initialize internal data if not exists
                if (!attendanceData[emp.employee_id]) {
                    attendanceData[emp.employee_id] = {
                        employee_id: emp.employee_id,
                        status: 'A',
                        in_time: defaultIn,
                        out_time: defaultOut,
                        tools_count: 0,
                        tools_details: '',
                        remarks: emp.designation || ''
                    };
                }
            });
        }

        function handleStatusChange(select, empId) {
            const status = select.value;
            attendanceData[empId].status = status;
            
            // Update color class dynamically
            select.className = `status-select status-${status}`;
            
            const row = select.closest('tr');
            const timeInputs = row.querySelectorAll('input[type="time"]');
            const disabled = (status !== 'P' && status !== 'HD');
            timeInputs.forEach(input => input.disabled = disabled);
            autoSave();
        }

        function updateField(empId, field, value) {
            attendanceData[empId][field] = value;
            autoSave();
        }

        let saveTimeout;
        function autoSave() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                saveAttendance();
            }, 500); // 500ms debounce
        }

        async function saveAttendance() {
            const date = document.getElementById('datePicker').value;
            const payload = Object.values(attendanceData).map(item => ({
                ...item,
                date: date
            }));

            try {
                const res = await fetch('http://localhost:5000/api/attendance/mark', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                
                if (result.success) {
                    // Quietly save without showing the popup, but maybe update a small non-intrusive UI if needed.
                    // For now, removing the toast to keep it silent as requested.
                }
            } catch (err) {
                console.error("Failed to auto-save", err);
            }
        }


        // Event Listeners
        document.getElementById('employeeSearch').addEventListener('input', (e) => renderTable(e.target.value));
        document.getElementById('datePicker').addEventListener('change', async (e) => {
            const newDate = e.target.value;
            document.getElementById('displayDate').innerText = newDate;
            await fetchExistingAttendance(newDate);
            renderTable();
        });

        init();
