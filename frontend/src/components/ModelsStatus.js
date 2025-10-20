import React, { useEffect, useState } from 'react';
import Spinner from './Spinner';

export default function ModelsStatus({ pollInterval = 3000 }) {
  const [status, setStatus] = useState({ transformers_available: false, summarizer_ready: false, generator_ready: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    let timer = null;

    const fetchStatus = async () => {
      try {
        const res = await fetch('http://localhost:5000/models/status');
        if (!mounted) return;
        const data = await res.json();
        setStatus(data);
        setLoading(false);
        if (!data.summarizer_ready || !data.generator_ready) {
          timer = setTimeout(fetchStatus, pollInterval);
        }
      } catch (e) {
        if (!mounted) return;
        setLoading(false);
        // retry
        timer = setTimeout(fetchStatus, pollInterval);
      }
    };

    fetchStatus();
    return () => {
      mounted = false;
      if (timer) clearTimeout(timer);
    };
  }, [pollInterval]);

  if (loading) return <div style={{ display: 'inline-flex', alignItems: 'center' }}><Spinner size={16} /> <span style={{ marginLeft: 8 }}>Checking models...</span></div>;
  if (status.summarizer_ready && status.generator_ready) return <div style={{ color: 'green', display: 'inline-flex', alignItems: 'center' }}>✅ <span style={{ marginLeft: 8 }}>Models ready</span></div>;
  if (status.transformers_available) return <div style={{ color: 'orange', display: 'inline-flex', alignItems: 'center' }}><Spinner size={14} /> <span style={{ marginLeft: 8 }}>Models loading...</span></div>;
  return <div style={{ color: 'gray', display: 'inline-flex', alignItems: 'center' }}>⚪ <span style={{ marginLeft: 8 }}>Models disabled (mock mode)</span></div>;
}
