
import VideoStream from './components/VideoStream';
import PoseLog from './components/PoseLog';
import ModeControl from './components/ModeControl';
import RunControl from './components/runControl';
import Forklift from './components/Forklift';

const App = () => {
  return (
    <div>
      <h1>Real-Time Pose and Video Streaming</h1>
      <div>
        <VideoStream />
        <div>
          <ModeControl />
          <RunControl />
          <Forklift/>
          <PoseLog />
        </div>
      </div>
    </div>
  );
};

export default App;