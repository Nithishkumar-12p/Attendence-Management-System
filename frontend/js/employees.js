        let allLabours = [];

        async function fetchEmployees() {
            const res = await fetch('http://localhost:5000/api/employees/');
            allLabours = await res.json();
            renderTable();
        }

        function renderTable(searchTerm = '') {
            const tbody = document.getElementById('employeeListBody');
            
            const filtered = allLabours.filter(lab => 
                String(lab.name).toLowerCase().includes(searchTerm.toLowerCase()) || 
                String(lab.employee_id).toLowerCase().includes(searchTerm.toLowerCase())
            );

            tbody.innerHTML = filtered.map(emp => `
                <tr>
                    <td>${emp.employee_id}</td>
                    <td style="font-weight: 600;">${emp.name}</td>
                    <td style="color: var(--text-dim);">${emp.designation || '-'}</td>
                    <td style="font-weight: 600; color: var(--primary);">₹${emp.basic_salary.toLocaleString()}</td>
                    <td>
                        <span class="badge ${emp.is_active ? 'badge-present' : 'badge-absent'}">
                            ${emp.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td style="text-align: right; padding-right: 2rem;">
                        <button class="btn" style="background: rgba(56, 189, 248, 0.1); color: var(--accent); padding: 0.3rem 0.6rem; margin-right: 0.5rem;" 
                                onclick='showEditModal(${JSON.stringify(emp)})'>Edit</button>
                        <button class="btn" style="background: rgba(239, 68, 68, 0.1); color: var(--danger); padding: 0.3rem 0.6rem;" 
                                onclick="deleteEmployee('${emp.employee_id}')">End Contract</button>
                    </td>
                </tr>
            `).join('');
        }

        document.getElementById('labourSearch').addEventListener('input', (e) => {
            renderTable(e.target.value);
        });

        async function deleteEmployee(empId) {
            if (confirm(`Are you sure you want to remove ${empId}?`)) {
                await fetch(`http://localhost:5000/api/employees/delete/${empId}`, { method: 'DELETE' });
                fetchEmployees();
            }
        }

        let isEditing = false;
        let currentEditId = '';

        function showAddModal() {
            isEditing = false;
            document.getElementById('addEmpModal').style.display = 'flex';
            document.getElementById('modalTitle').innerText = 'Register New Labour';
            document.getElementById('addEmpForm').reset();
        }

        function showEditModal(emp) {
            isEditing = true;
            currentEditId = emp.employee_id;
            document.getElementById('addEmpModal').style.display = 'flex';
            document.getElementById('modalTitle').innerText = 'Edit Labour Details';
            
            document.getElementById('empName').value = emp.name;
            document.getElementById('empDesignation').value = emp.designation || '';
            document.getElementById('empSalary').value = emp.basic_salary;
            document.getElementById('empAadhar').value = emp.aadhar_number || '';
            document.getElementById('empPhone').value = emp.phone_number || '';
            document.getElementById('empContractStart').value = emp.contract_start_date || '';
            document.getElementById('empContractEnd').value = emp.contract_end_date || '';
            document.getElementById('empHours').value = emp.working_hours_per_day || 8;
        }

        function hideAddModal() {
            document.getElementById('addEmpModal').style.display = 'none';
        }

        document.getElementById('addEmpForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById('empName').value,
                designation: document.getElementById('empDesignation').value,
                basic_salary: parseFloat(document.getElementById('empSalary').value),
                aadhar_number: document.getElementById('empAadhar').value,
                phone_number: document.getElementById('empPhone').value,
                contract_start_date: document.getElementById('empContractStart').value,
                contract_end_date: document.getElementById('empContractEnd').value,
                working_hours_per_day: parseFloat(document.getElementById('empHours').value)
            };

            const url = isEditing ? `http://localhost:5000/api/employees/update/${currentEditId}` : 'http://localhost:5000/api/employees/add';
            const method = isEditing ? 'PUT' : 'POST';

            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await res.json();
            if (result.success) {
                hideAddModal();
                fetchEmployees();
            } else {
                alert("Operation failed. Please try again.");
            }
        });

        fetchEmployees();
