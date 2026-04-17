        async function generateSalaries() {
            const month = parseInt(document.getElementById('reportMonth').value);
            const year = parseInt(document.getElementById('reportYear').value);
            const btn = document.getElementById('genBtn');
            
            btn.disabled = true;
            btn.innerText = 'Calculating...';

            try {
                // First get all employee IDs
                const empRes = await fetch('http://localhost:5000/api/employees/');
                if (!empRes.ok) throw new Error("Failed to fetch employees");
                const emps = await empRes.json();
                const ids = emps.map(e => e.employee_id);

                // Run calculation
                const calcRes = await fetch('http://localhost:5000/api/salary/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ employee_ids: ids, month, year })
                });
                
                if (!calcRes.ok) throw new Error("Salary calculation failed");

                alert("Salaries generated successfully for all employees.");
                fetchReport();
            } catch (err) {
                console.error(err);
                alert("Error generating salaries: " + err.message);
            } finally {
                btn.disabled = false;
                btn.innerText = 'Generate / Refresh Salaries';
            }
        }

        async function fetchReport() {
            const month = document.getElementById('reportMonth').value;
            const year = document.getElementById('reportYear').value;
            const monthName = document.getElementById('reportMonth').options[document.getElementById('reportMonth').selectedIndex].text;
            
            document.getElementById('reportTitle').innerText = `Payroll Report - ${monthName} ${year}`;
            
            try {
                const res = await fetch(`http://localhost:5000/api/salary/report/${month}/${year}`);
                if (!res.ok) throw new Error("Failed to fetch salary report");
                const data = await res.json();
                
                const tbody = document.getElementById('salaryBody');
                tbody.innerHTML = '';
                
                let totalPay = 0;

                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-dim); padding: 2rem;">No salary data found for this month. <br><small>Click <b>Generate</b> above to calculate.</small></td></tr>';
                    document.getElementById('totalPayout').innerText = '₹0';
                } else {
                    data.forEach(r => {
                        totalPay += r.final_salary;
                        
                        tbody.innerHTML += `
                            <tr>
                                <td style="color:var(--text-dim)">${r.employee_id}</td>
                                <td style="font-weight: 600;">${r.name}</td>
                                <td>₹${Number(r.basic_salary).toLocaleString()}</td>
                                <td style="text-align: center;">${r.present_days}</td>
                                <td style="text-align: center;">${r.absent_days}</td>
                                <td style="font-weight: 700; color: var(--success);">₹${Number(r.final_salary).toLocaleString()}</td>
                            </tr>
                        `;
                    });
                    document.getElementById('totalPayout').innerText = `₹${totalPay.toLocaleString()}`;
                    filterSalaries(); // Re-apply current search if any
                }
            } catch (err) {
                console.error(err);
                alert("Error fetching report: " + err.message);
            }
        }

        // ─── Search & Filtering ───────────────────────────────────────────
        function filterSalaries() {
            const term = document.getElementById('salarySearch').value.toLowerCase();
            const clearBtn = document.getElementById('clearSalarySearch');
            const rows = document.querySelectorAll('#salaryBody tr');
            
            if (clearBtn) clearBtn.style.display = term ? 'block' : 'none';

            let filteredTotal = 0;

            rows.forEach(row => {
                const name = row.cells[1]?.innerText.toLowerCase() || "";
                const id = row.cells[0]?.innerText.toLowerCase() || "";
                const isMatch = name.includes(term) || id.includes(term);
                
                if (isMatch) {
                    row.style.display = '';
                    // Extract salary value: remove '₹' and commas, then parse
                    const salaryText = row.cells[5]?.innerText.replace(/[₹,]/g, '') || "0";
                    filteredTotal += parseFloat(salaryText);
                } else {
                    row.style.display = 'none';
                }
            });

            // Update the UI total
            const totalEl = document.getElementById('totalPayout');
            if (totalEl) {
                totalEl.innerText = `₹${filteredTotal.toLocaleString()}`;
            }
        }

        function clearSearch() {
            document.getElementById('salarySearch').value = '';
            filterSalaries();
            document.getElementById('salarySearch').focus();
        }

        // ─── Exports ──────────────────────────────────────────────────────
        function exportFullReport() {
            const m = document.getElementById('reportMonth').value;
            const y = document.getElementById('reportYear').value;
            
            // Collect IDs of employees currently visible in the table (results of search/filter)
            const visibleRows = document.querySelectorAll('#salaryBody tr:not([style*="display: none"])');
            const ids = Array.from(visibleRows)
                             .map(tr => tr.cells[0].innerText.trim())
                             .filter(id => id && id !== "");

            let url = `http://localhost:5000/api/reports/pdf/salary/${m}/${y}`;
            if (ids.length > 0) {
                url += `?ids=${ids.join(',')}`;
            }
            
            window.location.href = url;
        }

        function downloadSlip(emp_id) {
            // Optional: keeping it just for internal logic if needed, but UI is removed
            const m = document.getElementById('reportMonth').value;
            const y = document.getElementById('reportYear').value;
            window.location.href = `http://localhost:5000/api/reports/pdf/salary/slip/${emp_id}/${m}/${y}`;
        }

        // Initial load
        fetchReport();
