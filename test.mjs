import { io } from "socket.io-client";

const socket = io("http://192.168.99.193:8888");

socket.emit("generate", { prompt: "41", model: "deepseek-r1:7b" });

socket.on("token", (data) => {
  console.log("Got token:", data);
});

socket.on("end", () => {
  console.log("Stream finished");
});
