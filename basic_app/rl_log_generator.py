import os
import numpy as np
import matplotlib.pyplot as plt
import json
from io import BytesIO
import base64

# Dynamically resolve 'static/dashboard_outputs/RL_Results'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This script's directory
STATIC_DIR = os.path.join(BASE_DIR, "..", "..", "static")
OUTPUT_DIR = os.path.join(STATIC_DIR, "dashboard_outputs", "RL_Results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_rl_log():
    try:
        episodes = list(range(1, 21))

        # Simulated allocation behavior
        btc = np.clip(np.linspace(0.1, 0.5, 20) + np.random.normal(0, 0.05, 20), 0, 1)
        eth = np.clip(np.linspace(0.5, 0.3, 20) + np.random.normal(0, 0.05, 20), 0, 1)
        sol = 1 - btc - eth

        # Normalize to sum to 1
        total = btc + eth + sol
        btc /= total
        eth /= total
        sol /= total

        # Simulate rewards
        rewards = np.cumsum(np.random.normal(loc=0.02, scale=0.01, size=20))

        # Save JSON log
        log_data = {
            "episodes": episodes,
            "allocations": {
                "BTC": btc.tolist(),
                "ETH": eth.tolist(),
                "SOL": sol.tolist()
            },
            "rewards": rewards.tolist()
        }

        with open(os.path.join(OUTPUT_DIR, "rl_episode_log.json"), "w") as f:
            json.dump(log_data, f, indent=2)

        # Reward plot
        plt.figure(figsize=(10, 4))
        plt.plot(episodes, rewards, marker='o', label="Cumulative Reward")
        plt.title("RL Agent: Cumulative Reward Over Episodes")
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.legend()
        plt.grid(True)

        reward_img_path = os.path.join(OUTPUT_DIR, "rl_reward_plot.png")
        plt.savefig(reward_img_path)
        plt.close()

        with open(reward_img_path, "rb") as f:
            reward_b64 = base64.b64encode(f.read()).decode("utf-8")
        with open(os.path.join(OUTPUT_DIR, "rl_reward_plot.txt"), "w") as f:
            f.write(reward_b64)

        # Allocation stackplot
        plt.stackplot(episodes, btc, eth, sol, labels=["BTC", "ETH", "SOL"], alpha=0.8)
        plt.title("RL Agent: Asset Allocation Over Episodes")
        plt.xlabel("Episode")
        plt.ylabel("Allocation")
        plt.legend(loc="upper left")
        plt.grid(True)

        alloc_img_path = os.path.join(OUTPUT_DIR, "rl_allocation_plot.png")
        plt.savefig(alloc_img_path)
        plt.close()

        with open(alloc_img_path, "rb") as f:
            alloc_b64 = base64.b64encode(f.read()).decode("utf-8")
        with open(os.path.join(OUTPUT_DIR, "rl_allocation_plot.txt"), "w") as f:
            f.write(alloc_b64)

        print("✅ RL simulation results saved to static/dashboard_outputs/RL_Results/")
    except Exception as e:
        print(f"❌ Error during RL log generation: {e}")

if __name__ == "__main__":
    generate_rl_log()
