import { io } from "socket.io-client";
import $ from "./jquery.ts";

type CommandType = "ai" | "rcon";
type CommandExitCode = "sent" | "empty";

interface Command {
  type: CommandType;
  message: string;
}

interface QueueItem {
  username: string;
  message: string;
  is_system: boolean;
}
interface QueueAction {
  index: number;
  action: string;
}

interface PanelVars {
  kill_switch?: boolean;
  auto_disable_voice?: boolean;
}

const socket = io({ autoConnect: false });

let last_queue: QueueItem[];
let last_console = "";

let console_scrolls = 0;

function action_link(index: number, action: string, text: string) {
  return $("<a>")
    .addClass("fakelink")
    .attr("draggable", "")
    .on("click", function () {
      socket.emit(
        "queue_action",
        {
          index: index,
          action: action,
        } as QueueAction,
      );
    })
    .text(text);
}

function init_pvars() {
  const update_pvars = (pvars: PanelVars) => {
    if ("kill_switch" in pvars) {
      $("#kill_switch").prop("checked", pvars.kill_switch);
    }
    if ("auto_disable_voice" in pvars) {
      $("#auto_disable_voice").prop("checked", pvars.auto_disable_voice);
    }
  };

  $(".pvar").on(
    "change",
    (event) => {
      socket.emit(
        "set_pvars",
        {
          kill_switch: $("#kill_switch").is(":checked"),
          auto_disable_voice: $("#auto_disable_voice").is(":checked"),
        } as PanelVars,
      );
    },
  );

  socket.on("broadcast_pvars", update_pvars);
}

function init_queue() {
  const broadcast_queue = (queue: QueueItem[]) => {
    if (JSON.stringify(queue) == JSON.stringify(last_queue)) return;

    $("#queuelength").text(
      `${queue.length} request${queue.length == 1 ? "" : "s"}`,
    );
    $("#queue>tbody").empty();

    queue.forEach((item, index) => {
      $("#queue>tbody").append(
        $("<tr>")
          .append(
            $("<td>").append($("<span>").text(item.username)),
          )
          .append(
            $("<td>").append($("<span>").text(item.message)),
          )
          .append(
            $("<td>")
              .append(action_link(index, "delete", "delete"))
              .appendText(". swap with ")
              .append(action_link(index, "swap_up", "above"))
              .appendText(" or ")
              .append(action_link(index, "swap_down", "below"))
              .appendText(". send to ")
              .append(action_link(index, "front", "front"))
              .appendText(" or ")
              .append(action_link(index, "back", "back"))
              .appendText(" of queue."),
          ),
      );
    });

    last_queue = queue;
  };

  socket.on("broadcast_queue", broadcast_queue);
}

function init_console() {
  const get_console = (console: string) => {
    if (last_console == console) return;
    $("#console #box").text(console);
    last_console = console;
    if (console_scrolls == 0) {
      $("#console").scrollTop(
        $("#console")[0].scrollHeight - $("#console")[0].clientHeight,
      );
    }
    console_scrolls++;
  };

  socket.on("broadcast_console", get_console);
}

$(async function () {
  async function send_cmd(
    type: CommandType,
    message: string,
  ): Promise<CommandExitCode> {
    if (message.trim() == "") {
      return "empty";
    }
    const response = await fetch("/cmd", {
      method: "POST",
      body: JSON.stringify({ type, message } as Command),
      headers: {
        "Content-Type": "application/json",
      },
    });
    return "sent";
  }

  const cmd_event_button = async (type: CommandType, message: string) => {
    const exitCode = await send_cmd(type, message);
    switch (exitCode) {
      case "sent":
        $("#statusline").text("sent!");
        break;
      case "empty":
        $("#statusline").text("empty command");
        break;
    }
  };

  $("#aicmd_send").on(
    "click",
    () => {
      cmd_event_button("ai", String($("#aicmd_text").val()));
    },
  );

  init_pvars();
  init_queue();
  init_console();

  socket.on("connected_count", (count: number) => {
    $("#connected_count").text(count);
  });

  socket.connect();
});
