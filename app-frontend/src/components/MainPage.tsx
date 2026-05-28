import React, { useState, useEffect, } from 'react';
import { Menu, X, Loader2, Plus, FileText, ChevronRight } from 'lucide-react';
import type {FusionJob} from '../types';
import Recipe from './Recipe';
import {exampleJob} from '../constants';
import { retrieveInference, sendInferenceRequest } from '../scripts/inference_utils';


const loadInitialJobs = (): FusionJob[] => {
  if (typeof window === 'undefined') return [];
  const savedJobs = localStorage.getItem('recipeFusionJobs');
  console.log("Loaded jobs from localStorage:", savedJobs);
  if (!savedJobs) return [exampleJob];
  
  try {
    return JSON.parse(savedJobs);
  } catch (e) {
    console.error("Failed to parse jobs from local storage", e);
    return [];
  }
};

// --- Main Page Component ---
export default function MainPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [jobs, setJobs] = useState<FusionJob[]>(loadInitialJobs);
  const [activeJobId, setActiveJobId] = useState<string | 'new'>('new');
  
  const [cuisineA, setCuisineA] = useState('');
  const [cuisineB, setCuisineB] = useState('');
  const [modelName, setModelName] = useState(import.meta.env.VITE_QWEN_MODELNAME);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 2. Persist to LocalStorage whenever jobs change
  useEffect(() => {
    localStorage.setItem('recipeFusionJobs', JSON.stringify(jobs));
    console.log("Saved jobs to localStorage:", jobs);
  }, [jobs]);

  // 3. Polling Mechanism for pending jobs
  useEffect(() => {
    const pendingJobs = jobs.filter(job => job.status === 'pending');
    if (pendingJobs.length === 0) {
      console.log("No pending jobs found:", jobs);
      return;
    }

    const pollInterval = setInterval(() => {
      pendingJobs.forEach(async (job) => {
        try {
          // Note: Browsers cannot natively fetch 's3://' URIs. 
          // You will either need an API Gateway/FastAPI proxy endpoint to check this, 
          // or return a presigned HTTPS URL from your SageMaker invocation.
        //   const response = await new Promise<{ ok: boolean, json: () => Promise<any>, status: number }>(resolve => 
        // setTimeout(() => resolve({ ok: true, json: () => Promise.resolve(DUMMY_RESPONSE), status: 200 }), 1000)
        console.log("Making an inference request for job:", job.id);
        const response = await retrieveInference(job.id);
        const resultData = response
        setJobs(currentJobs => 
            currentJobs.map(j => 
            j.id === job.id 
                ? { ...j, status: 'completed', resultData } 
                : j
            )
        );
        } catch (error) {
          console.error(`Error polling job ${job.id}:`, error);
          // console.error('Using DUMMY_RESPONSE for testing purposes.');
        //   setJobs(currentJobs => 
        //     currentJobs.map(j => 
        //     j.id === job.id 
        //         ? { ...j, status: 'completed', resultData: DUMMY_RESPONSE } 
        //         : j
        //     )
        // );
        }
      });
    }, 60000); // Poll every 60 seconds

    return () => clearInterval(pollInterval);
  }, [jobs]);

  const handleSubmit = async (e: React.SubmitEvent) => {
    e.preventDefault();
    if (!cuisineA.trim() || !cuisineB.trim()) return;

    setIsSubmitting(true);
    try {
      // Mocking the SageMaker Async Endpoint call
      // Replace with your actual fetch call to SageMaker or your FastAPI backend
      const response_data = await sendInferenceRequest(cuisineA, cuisineB, modelName);

      const newJob: FusionJob = {
        id: response_data.id,
        cuisineA,
        cuisineB,
        modelName,
        s3OutputPath: "None",
        status: 'pending',
        timestamp: Date.now(),
      };

      setJobs(prev => [newJob, ...prev]);
      setActiveJobId(newJob.id);
      setCuisineA('');
      setCuisineB('');
    } catch (error) {
      console.error("Failed to start inference", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const activeJob = jobs.find(j => j.id === activeJobId);

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden font-sans">
      {/* Sidebar */}
      <div 
        className={`${isSidebarOpen ? 'w-72' : 'w-0'} transition-all duration-300 ease-in-out bg-gray-900 text-white flex flex-col overflow-hidden shrink-0`}
      >
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <h1 className="font-bold text-lg whitespace-nowrap">RecipeFusion</h1>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <button
            onClick={() => setActiveJobId('new')}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeJobId === 'new' ? 'bg-indigo-600' : 'hover:bg-gray-800'}`}
          >
            <Plus size={18} />
            <span>New Fusion</span>
          </button>

          <div className="pt-6 pb-2">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">History</p>
          </div>

          {jobs.map(job => (
            <button
              key={job.id}
              onClick={() => setActiveJobId(job.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-sm transition-colors text-left ${activeJobId === job.id ? 'bg-gray-800 border-l-2 border-indigo-500' : 'hover:bg-gray-800'}`}
            >
              <div className="flex items-center gap-2 truncate">
                <FileText size={16} className="text-gray-400 shrink-0" />
                <span className="truncate" title={`${job.cuisineA} + ${job.cuisineB} (${job.modelName})`}>{job.cuisineA} + {job.cuisineB} ({job.modelName})</span>
              </div>
              {job.status === 'pending' && <Loader2 size={14} className="animate-spin text-indigo-400 shrink-0" />}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 shrink-0">
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 hover:bg-gray-100 rounded-md text-gray-600 transition-colors"
          >
            {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="ml-4 flex items-center gap-2 text-sm text-gray-500">
            <span>RecipeFusion</span>
            <ChevronRight size={14} />
            <span className="font-medium text-gray-900">
              {activeJobId === 'new' ? 'New Request' : 'View Results'}
            </span>
          </div>
        </header>

        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-5xl mx-auto">
            {activeJobId === 'new' ? (
              <div className="bg-white p-8 rounded-xl border border-gray-200 shadow-sm">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Create a Fusion Recipe</h2>
                <form onSubmit={handleSubmit} className="space-y-6">
                  
                  {/* Cuisine Inputs */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Cuisine A</label>
                      <input 
                        type="text"
                        placeholder="e.g., Italian"
                        value={cuisineA}
                        maxLength={30}
                        onChange={(e) => setCuisineA(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Cuisine B</label>
                      <input 
                        type="text"
                        placeholder="e.g., Japanese"
                        value={cuisineB}
                        maxLength={30}
                        onChange={(e) => setCuisineB(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                        required
                      />
                    </div>
                  </div>

                  {/* Model Selection Dropdown */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">AI Model</label>
                    <select
                      value={modelName}
                      onChange={(e) => setModelName(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none bg-white"
                      required
                    >
                      <option value={import.meta.env.VITE_QWEN_MODELNAME}>Qwen 4b finetuned</option>
                      <option value={import.meta.env.VITE_LLAMA_MODELNAME}>Llama 8b finetuned</option>
                    </select>
                  </div>

                  {/* Submit Button */}
                  <button 
                    type="submit"
                    disabled={isSubmitting || !cuisineA || !cuisineB}
                    className="w-full flex justify-center items-center gap-2 bg-indigo-600 text-white py-3 rounded-md font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isSubmitting ? (
                      <><Loader2 size={20} className="animate-spin" /> Starting Inference...</>
                    ) : (
                      'Generate Fusion Recipe'
                    )}
                  </button>
                </form>
              </div>
            ) : activeJob ? (
              activeJob.status === 'pending' ? (
                <div className="flex flex-col items-center justify-center h-64 bg-white rounded-xl border border-gray-200 border-dashed">
                  <Loader2 size={40} className="animate-spin text-indigo-500 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900">LLM Inference in Progress</h3>
                  <p className="text-gray-500 mt-2 text-center max-w-sm">
                    Fusing {activeJob.cuisineA} and {activeJob.cuisineB}. This typically takes about 5 minutes. You can safely navigate away; we'll keep checking.
                  </p>
                </div>
              ) : (
                <Recipe job={activeJob} />
              )
            ) : (
              <div className="text-center text-gray-500 mt-20">
                Job not found.
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}