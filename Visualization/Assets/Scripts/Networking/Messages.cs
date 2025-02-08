using System;
using System.Collections.Generic;

namespace Messages {
    [Serializable]
    public class AgentData {
        public int id;
        public int[] pos;
        public string type;
    }

    [Serializable]
    public class SimState
    {
        public int[] dims;
        public float[][] grid;
        public AgentData[] agents;
        public int[] deleted;
        internal IEnumerable<object> semaphores;
    }
}
