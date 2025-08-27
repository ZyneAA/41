import { io } from "socket.io-client";

const socket = io("http://172.90.2.133:8888");

socket.emit("generate", { prompt: "hi how are u", model: "deepseek-r1:7b" });

socket.on("token", (data) => {
  console.log("Got token:", data);
});

socket.on("end", () => {
  console.log("Stream finished");
});
