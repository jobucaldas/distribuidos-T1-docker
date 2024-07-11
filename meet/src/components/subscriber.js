import zmq from "zeromq"

export async function sub(id, name) {
    const sock = new zmq.Subscriber()

    sock.connect("ws://localhost:5556")
    sock.subscribe(id)
    console.log("Subscriber connected to port 5556")

    for await (const [topic, msg] of sock) {
        console.log(
        "received a message related to:",
        topic,
        "containing message:",
        msg,
        )
    }
}

export async function pub(id, name, message) {
    const sock = new zmq.Publisher()
  
    await sock.bind("ws://localhost:5555")
    console.log("Publisher bound to port 5555")
  
    while (true) {
      console.log("sending a multipart message envelope")
      await sock.send([id, message])
      await new Promise(resolve => {
        setTimeout(resolve, 500)
      })
    }
  }
  
