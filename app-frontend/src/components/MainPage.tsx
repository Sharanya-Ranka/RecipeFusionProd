import React, { useState, useEffect, } from 'react';
import { Menu, X, Loader2, Plus, FileText, ChevronRight } from 'lucide-react';
import type {FusionJob} from '../types';
import Recipe from './Recipe';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import {exampleJob} from '../constants'; // exampleJob2
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { retrieveInference, sendInferenceRequest } from '../scripts/inference_utils';

const MINUTE = 60000;
const TICK_TIME_INTERVAL = 0.5 * MINUTE; // Check every 30 seconds for pending jobs
const POLL_TIME_INTERVALS = [2 * MINUTE, 3 * MINUTE, 5 * MINUTE, 10 * MINUTE, 12 * MINUTE];
const MAX_TIME_BEFORE_FAIL = POLL_TIME_INTERVALS[POLL_TIME_INTERVALS.length - 1] + 2 * TICK_TIME_INTERVAL; // Mark as failed if pending for more than the longest poll interval + buffer

const loadInitialJobs = (): FusionJob[] => {
  if (typeof window === 'undefined') return [];
  const savedJobs = localStorage.getItem('recipeFusionJobs');
  // console.log("Loaded jobs from localStorage:", savedJobs);
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
  const [isFocused, setIsFocused] = useState<boolean>(
    document.visibilityState === 'visible' && document.hasFocus()
  );
  const [tick, setTick] = useState<number>(0);
  
  const [cuisineA, setCuisineA] = useState('');
  const [cuisineB, setCuisineB] = useState('');
  const [modelName, setModelName] = useState(import.meta.env.VITE_QWEN_MODELNAME);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 2. Persist to LocalStorage whenever jobs change
  useEffect(() => {
    localStorage.setItem('recipeFusionJobs', JSON.stringify(jobs));
    console.log("Saved jobs to localStorage:", jobs);
  }, [jobs]);

  useEffect(() => {
    const timer = setInterval(() => setTick(t => t + 1), TICK_TIME_INTERVAL);
    return () => clearInterval(timer);
  }, []);

  function retrieveInferenceMain(jobsToQuery: FusionJob[], mode:string) {
    console.log("Retrieving inference in mode:", mode);
    jobsToQuery.forEach(async (job) => {
        try {
        console.log("Making an inference request for job:", job.id);
        const response = await retrieveInference(job.id);

        if (!response) {
          console.warn(`Job ${job.id} is still pending (empty response). Will check again later.`);
          setJobs(currentJobs => 
            currentJobs.map(j => 
            j.id === job.id 
                ? { ...j, lastCheckTimestamp: Date.now()} 
                : j
            )
          ); 
        }
        else{
          const resultData = response
          setJobs(currentJobs => 
              currentJobs.map(j => 
              j.id === job.id 
                  ? { ...j, status: 'completed', resultData , lastCheckTimestamp: Date.now()} 
                  : j
              )
          );
        }
        } catch (error) {
          console.error(`Error polling job ${job.id}:`, error);
          setJobs(currentJobs => 
            currentJobs.map(j => 
            j.id === job.id 
                ? { ...j, lastCheckTimestamp: Date.now(), status: 'failed' } 
                : j
            )
        );
        }
      });
  }

  // 3. Polling Mechanism for pending jobs
  useEffect(() => {
    const pendingJobs = jobs.filter(job => job.status === 'pending');
    if (pendingJobs.length === 0) {
      console.log("No pending jobs found:", jobs);
      return;
    }
    const currentTime = Date.now();
    const jobsToQuery = pendingJobs.filter(job => {
      const timeRequestToLastCheck =  job.lastCheckTimestamp - job.requestSentTimestamp;
      const timeSinceRequest = currentTime - job.requestSentTimestamp;

      for(let i = 0; i < POLL_TIME_INTERVALS.length; i++) {
        if (timeRequestToLastCheck < POLL_TIME_INTERVALS[i] && timeSinceRequest >= POLL_TIME_INTERVALS[i]) {
          return true;
        }      
      }
    });

    const newFailedJobs = pendingJobs.filter(job => {
      const timeSinceRequest = currentTime - job.requestSentTimestamp;
      return timeSinceRequest > MAX_TIME_BEFORE_FAIL;
    })

    retrieveInferenceMain(jobsToQuery, 'polling');

    newFailedJobs.forEach(job => {
      console.error(`Job ${job.id} has failed due to timeout.`);
      setJobs(currentJobs => 
          currentJobs.map(j => 
          j.id === job.id 
              ? { ...j, lastCheckTimestamp: Date.now(), status: 'failed' } 
              : j
          )
      );
    });
      

    return;
  }, [tick]);

  useEffect(() => {
    if(!isFocused) return;
    const pendingJobs = jobs.filter(job => job.status === 'pending');
    if (pendingJobs.length === 0) {
      console.log("No pending jobs found:", jobs);
      return;
    }

    retrieveInferenceMain(pendingJobs, 'focus');
  }, [isFocused])

  useEffect(() => {
    const handleFocus = () => setIsFocused(true);
    const handleBlur = () => setIsFocused(false);
    
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        setIsFocused(true);
      } else {
        setIsFocused(false);
      }
    };

    // "Back to app" events
    window.addEventListener('focus', handleFocus);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // "Leaving app" events
    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('focus', handleFocus);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleBlur);
    };
  }, []);

  const handleSubmit = async (e: React.SubmitEvent) => {
    e.preventDefault();
    if (!cuisineA.trim() || !cuisineB.trim()) return;

    setIsSubmitting(true);
    try {
      // Mocking the SageMaker Async Endpoint call
      // Replace with your actual fetch call to SageMaker or your FastAPI backend
      const response_data = await sendInferenceRequest(cuisineA, cuisineB, modelName);
      // console.log("Received response from inference request:", response_data);
      const newJob: FusionJob = {
        id: response_data.id,
        cuisineA,
        cuisineB,
        modelName,
        status: 'pending',
        requestSentTimestamp: Date.now(),
        lastCheckTimestamp: Date.now(),
      };

      setJobs(prev => [newJob, ...prev]);
      // setNumJobs(prev => prev + 1);
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