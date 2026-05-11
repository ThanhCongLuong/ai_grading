import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = "http://localhost:8080";
function App() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewingFileId, setViewingFileId] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reviewContent, setReviewContent] = useState(null);
  const [activeId, setActiveId] = useState(null);
  const [editableFeedback, setEditableFeedback] = useState("");
  const modalStyles = {
    overlay: {
      position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.85)', zIndex: 9999,
      display: (viewingFileId || reviewContent) ? 'flex' : 'none',
      alignItems: 'center', justifyContent: 'center',
    },
    content: {
      width: '90%', height: '90%', backgroundColor: '#fff',
      position: 'relative', borderRadius: '8px', overflow: 'hidden',
    },
    closeBtn: {
      position: 'absolute', top: '10px', right: '10px', zIndex: 10001,
      backgroundColor: '#ff4d4f', color: 'white', border: 'none',
      padding: '8px 15px', cursor: 'pointer', borderRadius: '4px', fontWeight: 'bold'
    }
  };

  const fetchSubmissions = async (isFirstLoad = false) => {
    try {
      const res = await axios.get(`${API_BASE}/submissions`);
      setSubmissions(prevSubmissions => {
        if (JSON.stringify(res.data) !== JSON.stringify(prevSubmissions)) {
          return res.data;
        }
        return prevSubmissions;
      });
      if (isFirstLoad) setLoading(false);
    } catch (err) {
      console.error("Error fetching data:", err);
      if (isFirstLoad) setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubmissions(true);
    const interval = setInterval(() => fetchSubmissions(false), 5000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (id, finalContent) => {
    if (window.confirm(`Confirm approval and send this email ?`)) {
      try {
        const res = await axios.post(`${API_BASE}/approve/${id}`, {
          final_email_content: finalContent
        });
        if (res.status === 200) {
          alert("Success: Saved edits and sent email!");
          setReviewContent(null);
          fetchSubmissions(false);
        }
      } catch (err) {
        alert("Error: " + (err.response?.data?.error || "Cannot send the email"));
      }
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "---";
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('vi-VN', {
      hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric',
    }).format(date);
  };

  if (loading) return <div className="loading">Loading system data...</div>;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>My Approvals</h1>
      </header>

      <nav className="tab-navigation">
        <button className="tab-item active">Pending</button>
        <button className="tab-item">Approved</button>
      </nav>

      <div className="table-wrapper">
        <table className="approval-table">
          <thead>
            <tr>
              <th>Student Name</th>
              <th>Subject / File</th>
              <th>AI Score</th>
              <th>Status</th>
              <th>Submission Date</th>
              <th>Updated Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {submissions.map((item) => (
              <tr key={item.submission_id}>
                <td><div className="cell-content font-bold">{item.student_real_name}</div></td>
                <td><div className="cell-content file-link">{item.file_name}</div></td>
                <td><div className="cell-content score-cell">{item.ai_score}</div></td>
                <td>
                  <div className="cell-content">
                    <span className="status-badge">{item.status}</span>
                  </div>
                </td>
                <td><div className="cell-content">{formatDate(item.created_at)}</div></td>
                <td><div className="cell-content">{formatDate(item.updated_at)}</div></td>
                <td>
                  <div className="actions-cell">
                    {/* Nút VIEW gọi setViewingFileId */}
                    <button onClick={() => setViewingFileId(item.file_id)} className="btn btn-view">👁</button>
                    <button
                      onClick={() => {
                        setReviewContent(item.ai_feedback);
                        setActiveId(item.student_id);
                      }}
                      className="btn btn-refer"
                    >
                      ↺
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 1. MODAL VIEW PDF */}
      {viewingFileId && (
        <div className="modal-overlay" onClick={() => setViewingFileId(null)} style={{ ...modalStyles.overlay, display: 'flex' }}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={modalStyles.content}>
            <button onClick={() => setViewingFileId(null)} style={modalStyles.closeBtn}>X</button>
            <iframe
              src={`https://drive.google.com/file/d/${viewingFileId}/preview`}
              width="100%" height="100%" allow="autoplay" title="Drive Preview"
            ></iframe>
          </div>
        </div>
      )}

      {/* 3. MODAL REVIEW FEEDBACK (AI DRAFT) */}
      {reviewContent && (
        <div className="modal-overlay" style={{ ...modalStyles.overlay, display: 'flex' }}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ ...modalStyles.content, width: '700px', height: '85%', padding: '25px', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
              <h2 style={{ margin: 0, color: '#333' }}>Review & Edit Email Draft</h2>
              <button onClick={() => setReviewContent(null)} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#999' }}>×</button>
            </div>

            <div
              contentEditable={true}
              onBlur={(e) => setEditableFeedback(e.currentTarget.innerHTML)}
              style={{
                backgroundColor: '#f9f9f9',
                padding: '20px',
                borderRadius: '5px',
                border: '1px solid #ddd',
                lineHeight: '1.6',
                outline: 'none'
              }}
              dangerouslySetInnerHTML={{ __html: reviewContent }}
            />

            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={() => { setReviewContent(null); setEditableFeedback(""); }}
                style={{ padding: '10px 25px', backgroundColor: 'Black', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '10px' }}
              >
                Cancel
              </button>
              <button
                onClick={() => handleApprove(activeId, editableFeedback || reviewContent)}
                style={{ padding: '10px 25px', backgroundColor: 'Red', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
              >
                Approve & Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;