'use client';

import { useState, useEffect } from 'react';

interface Project {
  id: number;
  name: string;
  description: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const userData = localStorage.getItem('user');
      if (!userData) return;

      const user = JSON.parse(userData);
      const response = await fetch(`http://localhost:8000/api/projects?user_id=${user.id}`);
      const data = await response.json();

      if (data.projects) {
        setProjects(data.projects);
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    }
  };

  const createProject = async () => {
    if (!projectName.trim()) {
      const event = new CustomEvent('showToast', {
        detail: { message: 'Project name is required', type: 'error' }
      });
      window.dispatchEvent(event);
      return;
    }

    try {
      setLoading(true);
      const userData = localStorage.getItem('user');
      if (!userData) {
        const event = new CustomEvent('showToast', {
          detail: { message: 'Please login to create projects', type: 'error' }
        });
        window.dispatchEvent(event);
        return;
      }

      const user = JSON.parse(userData);
      const response = await fetch('http://localhost:8000/api/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: projectName,
          description: projectDescription,
          user_id: user.id,
          metadata: {}
        }),
      });

      if (response.ok) {
        const newProject = await response.json();
        setProjects([newProject, ...projects]);
        setProjectName('');
        setProjectDescription('');
        setShowCreateModal(false);

        // Show success toast
        const event = new CustomEvent('showToast', {
          detail: { message: `Created ${projectName}`, type: 'success' }
        });
        window.dispatchEvent(event);
      } else {
        const error = await response.json();
        const event = new CustomEvent('showToast', {
          detail: { message: error.error || 'Failed to create project', type: 'error' }
        });
        window.dispatchEvent(event);
      }
    } catch (error) {
      console.error('Failed to create project:', error);
      const event = new CustomEvent('showToast', {
        detail: { message: 'Failed to create project', type: 'error' }
      });
      window.dispatchEvent(event);
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (projectId: number, projectName: string) => {
    if (!confirm(`Are you sure you want to delete "${projectName}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/projects/${projectId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setProjects(projects.filter(p => p.id !== projectId));
        const event = new CustomEvent('showToast', {
          detail: { message: `Deleted ${projectName}`, type: 'success' }
        });
        window.dispatchEvent(event);
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
      const event = new CustomEvent('showToast', {
        detail: { message: 'Failed to delete project', type: 'error' }
      });
      window.dispatchEvent(event);
    }
  };

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Projects</h1>
            <p className="text-gray-400">Manage and organize your AI projects</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
          >
            + New Project
          </button>
        </div>

        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
          />
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <div
              key={project.id}
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all duration-200"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold">{project.name}</h3>
                <button
                  onClick={() => deleteProject(project.id, project.name)}
                  className="text-red-400 hover:text-red-300 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              <p className="text-gray-400 mb-4 line-clamp-2">
                {project.description || 'No description'}
              </p>
              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                <button className="text-blue-400 hover:text-blue-300 transition-colors">
                  Open →
                </button>
              </div>
            </div>
          ))}
        </div>

        {filteredProjects.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">No projects found</p>
            <p className="text-gray-500 mt-2">Create your first project to get started</p>
          </div>
        )}
      </div>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
          <div className="bg-[#1a1a1a] border border-white/10 rounded-lg p-8 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-6">Create New Project</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Project Name *</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="Enter project name"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Description (Optional)</label>
                <textarea
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  placeholder="Enter project description"
                  rows={4}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all resize-none"
                  disabled={loading}
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setProjectName('');
                  setProjectDescription('');
                }}
                className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-all"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                onClick={createProject}
                disabled={loading}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating...' : 'Create Project'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
