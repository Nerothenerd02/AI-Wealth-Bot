import os
import numpy as np
import matplotlib.pyplot as plt
import json

# Set a simpler output directory
OUTPUT_DIR = r"C:\Temp\RL_Results"

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
print(f"📂 Output directory: {OUTPUT_DIR}")  # Debugging output directory

def generate_stock_rl_log():
    try:
        episodes = list(range(1, 21))

        # Simulated allocation behavior for stocks
        aapl = np.clip(np.linspace(0.2, 0.5, 20) + np.random.normal(0, 0.03, 20), 0, 1)
        tsla = np.clip(np.linspace(0.5, 0.3, 20) + np.random.normal(0, 0.03, 20), 0, 1)
        msft = 1 - aapl - tsla

        # Normalize
        total = aapl + tsla + msft
        aapl /= total
        tsla /= total
        msft /= total

        rewards = np.cumsum(np.random.normal(loc=0.015, scale=0.01, size=20))

        # Save log data
        log_data = {
            "episodes": episodes,
            "allocations": {
                "AAPL": aapl.tolist(),
                "TSLA": tsla.tolist(),
                "MSFT": msft.tolist()
            },
            "rewards": rewards.tolist()
        }
        log_file_path = os.path.join(OUTPUT_DIR, "rl_stock_episode_log.json")
        with open(log_file_path, "w") as f:
            json.dump(log_data, f, indent=2)
        print(f"📁 Log file saved to: {log_file_path}")  # Debugging log file path

        # Plot rewards
        reward_img_path = os.path.join(OUTPUT_DIR, "rl_stock_reward_plot.png")
        plt.figure(figsize=(10, 4))
        plt.plot(episodes, rewards, marker='o', label="Cumulative Reward (Stocks)")
        plt.title("RL Agent: Cumulative Reward Over Episodes (Stocks)")
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.legend()
        plt.grid(True)
        plt.savefig(reward_img_path)
        plt.close()
        print(f"📊 Reward plot saved to: {reward_img_path}")  # Debugging reward plot path

        # Plot allocation
        alloc_img_path = os.path.join(OUTPUT_DIR, "rl_stock_allocation_plot.png")
        plt.stackplot(episodes, aapl, tsla, msft, labels=["AAPL", "TSLA", "MSFT"], alpha=0.8)
        plt.title("RL Agent: Stock Allocation Over Episodes")
        plt.xlabel("Episode")
        plt.ylabel("Allocation")
        plt.legend(loc="upper left")
        plt.grid(True)
        plt.savefig(alloc_img_path)
        plt.close()
        print(f"📊 Allocation plot saved to: {alloc_img_path}")  # Debugging allocation plot path

        print("✅ Stock RL simulation completed successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_stock_rl_log()