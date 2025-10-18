import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Label
} from 'recharts';

// Sample data showing weekly progress across three metrics
const sampleData = [
  { week: 'Week 1', mastery: 20, engagement: 30, accuracy: 60 },
  { week: 'Week 2', mastery: 35, engagement: 45, accuracy: 65 },
  { week: 'Week 3', mastery: 50, engagement: 55, accuracy: 70 },
  { week: 'Week 4', mastery: 60, engagement: 60, accuracy: 75 },
  { week: 'Week 5', mastery: 70, engagement: 68, accuracy: 78 },
  { week: 'Week 6', mastery: 78, engagement: 72, accuracy: 82 },
  { week: 'Week 7', mastery: 85, engagement: 78, accuracy: 88 },
];

const MetricChart = ({ title, children }) => (
  <div style={{ flex: 1, minWidth: 300, height: 260, padding: 12, boxSizing: 'border-box' }}>
    <h3 style={{ margin: '0 0 8px 0' }}>{title}</h3>
    <div style={{ width: '100%', height: 220 }}>{children}</div>
  </div>
);

export default function LearnerProgress({ data = sampleData }) {
  return (
    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
      <MetricChart title="Mastery Over Time">
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week">
              <Label value="Week" position="insideBottom" offset={-6} />
            </XAxis>
            <YAxis domain={[0, 100]}>
              <Label value="Mastery (%)" angle={-90} position="insideLeft" />
            </YAxis>
            <Tooltip formatter={(value) => `${value}%`} />
            <Legend />
            <Line
              type="monotone"
              dataKey="mastery"
              stroke="#4caf50"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </MetricChart>

      <MetricChart title="Engagement (Area)">
        <ResponsiveContainer>
          <AreaChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week">
              <Label value="Week" position="insideBottom" offset={-6} />
            </XAxis>
            <YAxis domain={[0, 100]}>
              <Label value="Engagement (%)" angle={-90} position="insideLeft" />
            </YAxis>
            <Tooltip formatter={(value) => `${value}%`} />
            <Legend />
            <Area
              type="monotone"
              dataKey="engagement"
              stroke="#2196f3"
              fill="#bbdefb"
              fillOpacity={0.6}
              isAnimationActive={true}
            />
          </AreaChart>
        </ResponsiveContainer>
      </MetricChart>

      <MetricChart title="Accuracy (Bar)">
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week">
              <Label value="Week" position="insideBottom" offset={-6} />
            </XAxis>
            <YAxis domain={[0, 100]}>
              <Label value="Accuracy (%)" angle={-90} position="insideLeft" />
            </YAxis>
            <Tooltip formatter={(value) => `${value}%`} />
            <Legend />
            <Bar dataKey="accuracy" fill="#ff9800" isAnimationActive={true} />
          </BarChart>
        </ResponsiveContainer>
      </MetricChart>
    </div>
  );
}
