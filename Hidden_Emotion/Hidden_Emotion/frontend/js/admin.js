class AdminManager {
  static async loadAdminDashboard() {
    const userTable = document.getElementById('adminUsersTableBody');
    const logsTable = document.getElementById('adminLogsTableBody');
    if (!userTable || !logsTable) return;

    const headers = window.AuthManager ? window.AuthManager.getAuthHeaders() : {};

    try {
      // 1. System status
      const statusRes = await fetch('/api/admin/system-status', { headers });
      if (statusRes.ok) {
        const data = await statusRes.ok ? await statusRes.json() : {};
        if (document.getElementById('sysDbStatus')) document.getElementById('sysDbStatus').innerText = data.database || 'Active';
        if (document.getElementById('sysUserCount')) document.getElementById('sysUserCount').innerText = data.users_count || 0;
        if (document.getElementById('sysDocCount')) document.getElementById('sysDocCount').innerText = data.documents_count || 0;
        if (document.getElementById('sysPredCount')) document.getElementById('sysPredCount').innerText = data.predictions_count || 0;
      }

      // 2. Users list
      const usersRes = await fetch('/api/admin/users', { headers });
      if (usersRes.ok) {
        const users = await usersRes.json();
        userTable.innerHTML = users.map(u => `
          <tr>
            <td><code class="text-info">${u.id}</code></td>
            <td class="fw-semibold text-light">${u.username}</td>
            <td>${u.email}</td>
            <td><span class="badge ${u.role === 'admin' ? 'bg-danger' : 'bg-primary'}">${u.role}</span></td>
            <td>${u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}</td>
          </tr>
        `).join('');
      }

      // 3. System logs
      const logsRes = await fetch('/api/admin/logs', { headers });
      if (logsRes.ok) {
        const logs = await logsRes.json();
        logsTable.innerHTML = logs.map(l => `
          <tr>
            <td><span class="badge ${l.level === 'ERROR' ? 'bg-danger' : 'bg-info'}">${l.level}</span></td>
            <td><span class="fw-semibold text-light">${l.event}</span></td>
            <td>${l.filename || l.details || '-'}</td>
            <td>${l.user || 'System'}</td>
            <td>${l.timestamp ? new Date(l.timestamp).toLocaleString() : 'Recent'}</td>
          </tr>
        `).join('');
      }
    } catch (err) {
      console.error("Error loading admin dashboard:", err);
    }
  }
}

window.AdminManager = AdminManager;
