        // Update time
        setInterval(() => {
            const now = new Date();
            document.getElementById('currentTime').innerText = now.toLocaleString();
        }, 1000);

        // Fetch dashboard stats
        async function fetchStats() {
            const today = new Date().toISOString().split('T')[0];
            try {
                const [empRes, attRes] = await Promise.all([
                    fetch('http://localhost:5000/api/employees/'),
                    fetch(`http://localhost:5000/api/attendance/list/${today}`)
                ]);
                
                const emps = await empRes.json();
                const atts = await attRes.json();
                
                document.getElementById('totalEmpCount').innerText = emps.length;
                
                // Count 'P' as 1 and 'HD' as 0.5 for the percentage, or just P+HD for headcount
                const presentCount = atts.filter(a => a.status === 'P' || a.status === 'HD').length;
                const late = atts.filter(a => a.is_late).length;
                const percent = emps.length > 0 ? Math.round((presentCount / emps.length) * 100) : 0;
                
                document.getElementById('todayPresentPercent').innerText = `${percent}%`;
                document.getElementById('todayLateCount').innerText = late;

                // Sort logically: those with an actual P/A status first, then by employee ID
                const sortedLogs = [...atts].sort((x, y) => {
                    const statusVal = { 'P': 1, 'HD': 2, 'CL': 3, 'SL': 4, 'A': 5 };
                    const sx = statusVal[x.status] || 99;
                    const sy = statusVal[y.status] || 99;
                    if (sx !== sy) return sx - sy;
                    return x.employee_id - y.employee_id;
                });

                // Inject table rows
                const tbody = document.querySelector('#recentLogTable tbody');
                tbody.innerHTML = sortedLogs.slice(0, 10).map(a => `
                    <tr>
                        <td>${a.name}</td>
                        <td>${a.remarks || a.designation || '-'}</td>
                        <td class="status-${a.status.toLowerCase()}">${a.status}</td>
                        <td>${a.in_time || '--:--'} ${a.is_late ? '<span class="status-late">LATE</span>' : ''}</td>
                        <td>${a.out_time || '--:--'}</td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error("Failed to fetch stats:", err);
            }
        }
        
        fetchStats();
