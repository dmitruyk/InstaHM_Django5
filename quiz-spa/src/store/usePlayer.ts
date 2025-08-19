import { create } from "zustand";

type PlayerState = { player_uuid: string; ensure(): string };

export const usePlayer = create<PlayerState>((set, get) => ({
  player_uuid: localStorage.getItem("player_uuid") || "",
  ensure() {
    let id = get().player_uuid;
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem("player_uuid", id);
      set({ player_uuid: id });
    }
    return id;
  }
}));
