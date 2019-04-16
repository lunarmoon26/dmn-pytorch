import {
  Directive,
  ElementRef,
  OnInit,
  Output,
  EventEmitter,
  OnDestroy
} from '@angular/core';
import * as PIXI from 'pixi.js';
import { BehaviorSubject } from 'rxjs';

const UNIT = 32;
const GAME_HEIGHT = 512;
const GAME_WIDTH = 512;
const MOVE_SPEED = 4;
const DEBUG_COLOR = 0xffff00;
const DEBUG_ALPHA = 0;

@Directive({
  selector: '[appGame]'
})
export class GameDirective implements OnInit, OnDestroy {
  @Output() sendMessage = new EventEmitter<string>();

  private maps = {};
  private doors = {};
  private player;
  private treasure;
  private treasureAt = 0;
  private rightBound = 0;
  private leftBound = 0;
  private upperBound = 0;
  private lowerBound = 0;
  private currentRoom = 0;
  private previousRoom = 0;

  private app: PIXI.Application;
  private controls = [];
  private pickedUp = false;
  private canPickUp = false;
  private shouldSwitch = false;

  constructor(private el: ElementRef) {}

  ngOnInit(): void {
    this.app = new PIXI.Application(GAME_WIDTH, GAME_HEIGHT, {
      backgroundColor: 0x1099bb
    });
    this.el.nativeElement.appendChild(this.app.view);

    if (!PIXI.loader.resources['assets/treasureHunter.json']) {
      PIXI.loader.add('assets/treasureHunter.json').load(() => {
        this.setup();
      });
    } else {
      PIXI.loader.resources['assets/treasureHunter.json'].load(() => {
        this.setup();
      });
    }
  }

  ngOnDestroy(): void {
    // PIXI.loader.reset();
    this.app.destroy();
    this.controls.forEach(c => {
      c.unsubscribe();
    });
  }

  setupMap() {
    this.app.stage.removeChildren();
    const map = this.maps[this.currentRoom];
    this.app.stage.addChild(map);
    this.rightBound = map.x + map.width - 42.5;
    this.leftBound = map.x + 42.5;
    this.upperBound = map.y + UNIT;
    this.lowerBound = map.y + map.height - 48;
  }
  setupObjects() {
    const from = this.previousRoom;
    const to = this.currentRoom;
    const map = this.maps[to];

    if (to === this.treasureAt) {
      this.app.stage.addChild(this.treasure);
    }

    this.player.vx = 0;
    this.player.vy = 0;
    this.player.x = 48;
    if (to === 2 || (from === 0 && to === 1)) {
      this.player.y = map.y + map.height - 42.5;
    } else {
      this.player.y = UNIT;
    }
    this.app.stage.addChild(this.player);
  }

  teleportTarget() {
    const room = this.currentRoom;
    if (room === 2) {
      if (this.contains(this.doors[room][0], this.player)) {
        return 1;
      }
    } else if (room === 1) {
      if (this.contains(this.doors[room][0], this.player)) {
        return 2;
      }
      if (this.contains(this.doors[room][1], this.player)) {
        return 0;
      }
    } else {
      if (this.contains(this.doors[room][0], this.player)) {
        return 1;
      }
    }
    return -1;
  }

  loadTextures() {
    this.maps[2] = new PIXI.Container();
    const kitch1 = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures['kitch1.png']
    );
    const kitch2 = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures['kitch2.png']
    );
    const kitch3 = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures['kitch3.png']
    );
    kitch2.x = 224;
    kitch3.y = 224;
    const kitchDoor = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures['door.png']
    );
    kitchDoor.position.set(32, 224);
    const kitchDoorTrigger = new PIXI.Graphics();
    kitchDoorTrigger.beginFill(DEBUG_COLOR, DEBUG_ALPHA);
    kitchDoorTrigger.drawRect(kitchDoor.x, kitchDoor.y - UNIT, UNIT, UNIT);
    this.doors[2] = [
      new PIXI.Rectangle(kitchDoor.x, kitchDoor.y - UNIT, UNIT, UNIT)
    ];

    const kitchText = new PIXI.Text('Kitchen', {
      fontFamily: 'Arial',
      fontSize: 48,
      fill: 0x0F0F0F,
      align: 'center'
    });
    // kitchText.anchor.set(0.5, 0.5);
    kitchText.position.set(UNIT, UNIT);
    kitchText.alpha = 0.5;
    this.maps[2].addChild(
      kitch1,
      kitch2,
      kitch3,
      kitchDoor,
      kitchDoorTrigger,
      kitchText
    );

    this.maps[0] = new PIXI.Container();
    const dungeon = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures[
        'dungeon.png'
      ]
    );
    const officeDoor = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures['door.png']
    );
    officeDoor.position.set(32, 0);
    const officeDoorTrigger = new PIXI.Graphics();
    officeDoorTrigger.beginFill(DEBUG_COLOR, DEBUG_ALPHA);
    officeDoorTrigger.drawRect(
      officeDoor.x,
      officeDoor.y + UNIT / 2,
      UNIT,
      UNIT
    );
    this.doors[0] = [
      new PIXI.Rectangle(officeDoor.x, officeDoor.y + UNIT / 2, UNIT, UNIT)
    ];
    const officeText = new PIXI.Text('Office', {
      fontFamily: 'Arial',
      fontSize: 72,
      fill: 0x0f0f0f,
      align: 'center'
    });
    officeText.pivot.set(0.5, 0.5);
    // kitchText.anchor.set(0.5, 0.5);
    officeText.position.set(UNIT, UNIT);
    officeText.alpha = 0.5;
    this.maps[0].addChild(dungeon, officeDoor, officeDoorTrigger, officeText);

    this.maps[1] = new PIXI.Container();
    const hallway1 = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures[
        'hallway1.png'
      ]
    );
    const hallway2 = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures[
        'hallway2.png'
      ]
    );
    hallway2.x = 64;
    const hallwayDoor1 = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures['door.png']
    );
    const hallwayDoor2 = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures['door.png']
    );
    hallwayDoor1.position.set(32, 0);
    hallwayDoor2.position.set(32, 480);
    const hallwayDoor1Trigger = new PIXI.Graphics();
    hallwayDoor1Trigger.beginFill(DEBUG_COLOR, DEBUG_ALPHA);
    hallwayDoor1Trigger.drawRect(
      hallwayDoor1.x,
      hallwayDoor1.y + UNIT / 2,
      UNIT,
      UNIT
    );
    const hallwayDoor2Trigger = new PIXI.Graphics();
    hallwayDoor2Trigger.beginFill(DEBUG_COLOR, DEBUG_ALPHA);
    hallwayDoor2Trigger.drawRect(
      hallwayDoor2.x,
      hallwayDoor2.y - UNIT,
      UNIT,
      UNIT
    );
    this.doors[1] = [
      new PIXI.Rectangle(hallwayDoor1.x, hallwayDoor1.y + UNIT / 2, UNIT, UNIT),
      new PIXI.Rectangle(hallwayDoor2.x, hallwayDoor2.y - UNIT, UNIT, UNIT)
    ];
    const hallwayText = new PIXI.Text('Hallway', {
      fontFamily: 'Arial',
      fontSize: 64,
      fill: 0x0f0f0f,
      align: 'center'
    });
    hallwayText.pivot.set(0, hallwayText.height);
    hallwayText.rotation = Math.PI / 2;
    hallwayText.alpha = 0.5;
    // kitchText.anchor.set(0.5, 0.5);
    hallwayText.position.set(UNIT, UNIT);
    this.maps[1].addChild(
      hallway1,
      hallway2,
      hallwayDoor1,
      hallwayDoor2,
      hallwayDoor1Trigger,
      hallwayDoor2Trigger,
      hallwayText
    );

    this.treasure = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures[
        'treasure.png'
      ]
    );
    this.treasure.anchor.set(0.5, 0.5);

    this.player = new PIXI.Container();
    const explorer = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures[
        'explorer.png'
      ]
    );
    explorer.anchor.set(0.5, 0.5);
    // this.player.x = 68;
    // this.player.y = this.app.stage.height / 2 - this.explorer.height / 2;
    this.player.vx = 0;
    this.player.vy = 0;
    this.player.addChild(explorer);
  }

  setup() {
    this.loadTextures();
    this.setupControls();
    this.setupMap();
    this.treasure.x = this.app.stage.width / 2;
    this.treasure.y = this.app.stage.height / 2;
    this.setupObjects();

    this.app.ticker.add(delta => {
      this.player.position.set(...this.clampPosition(this.player));
      this.shouldPickUpObject();
      this.shouldSwitchMap();
    });
  }

  clampPosition(o) {
    const clampX = Math.min(
      Math.max(o.x + o.vx, this.leftBound),
      this.rightBound
    );
    const clampY = Math.min(
      Math.max(o.y + o.vy, this.upperBound),
      this.lowerBound
    );
    return [clampX, clampY];
  }

  shouldPickUpObject() {
    const canPickUp = this.isColliding(this.player, this.treasure);
    if (this.canPickUp !== canPickUp) {
      this.canPickUp = canPickUp;
    }

    if (this.pickedUp && this.player.children.length === 1) {
      this.app.stage.removeChildAt(1);
      this.treasure.x = 0;
      this.treasure.y = -20;
      this.player.addChild(this.treasure);
    } else if (!this.pickedUp && this.player.children.length > 1) {
      this.player.removeChildAt(1);
      this.treasure.x = this.player.x;
      this.treasure.y = this.player.y;
      this.app.stage.addChildAt(this.treasure, 1);
    }
  }

  shouldSwitchMap() {
    if (this.shouldSwitch) {
      this.setupMap();
      this.setupObjects();
      this.shouldSwitch = false;
    }
  }

  setupControls() {
    // Capture the keyboard arrow keys
    const left = this.keyboard('a');
    const up = this.keyboard('w');
    const right = this.keyboard('d');
    const down = this.keyboard('s');
    const action = this.keyboard('e');
    const teleport = this.keyboard(' ');
    this.controls.push(left);
    this.controls.push(up);
    this.controls.push(right);
    this.controls.push(down);
    this.controls.push(action);
    this.controls.push(teleport);

    // Left arrow key `press` method
    left.press = () => {
      // Change the player's velocity when the key is pressed
      this.player.vx = -MOVE_SPEED;
      this.player.vy = 0;
    };

    // Left arrow key `release` method
    left.release = () => {
      // If the left arrow has been released, and the right arrow isn't down,
      // and the player isn't moving vertically:
      // Stop the player
      if (!right.isDown && this.player.vy === 0) {
        this.player.vx = 0;
      }
    };

    // Up
    up.press = () => {
      this.player.vy = -MOVE_SPEED;
      this.player.vx = 0;
    };
    up.release = () => {
      if (!down.isDown && this.player.vx === 0) {
        this.player.vy = 0;
      }
    };

    // Right
    right.press = () => {
      this.player.vx = MOVE_SPEED;
      this.player.vy = 0;
    };
    right.release = () => {
      if (!left.isDown && this.player.vy === 0) {
        this.player.vx = 0;
      }
    };

    // Down
    down.press = () => {
      this.player.vy = MOVE_SPEED;
      this.player.vx = 0;
    };
    down.release = () => {
      if (!up.isDown && this.player.vx === 0) {
        this.player.vy = 0;
      }
    };

    action.press = () => {
      if (!this.pickedUp && this.canPickUp) {
        this.pickedUp = true;
        this.treasureAt = -1;
        this.sendMessage.emit(`Jeff ${this.randomPickUp()} the apple there.`);
      } else if (this.pickedUp) {
        this.pickedUp = false;
        this.treasureAt = this.currentRoom;
        this.sendMessage.emit(`Jeff ${this.randomDrop()} the apple.`);
      }
    };

    teleport.press = () => {
      const target = this.teleportTarget();
      if (target !== -1) {
        this.previousRoom = this.currentRoom;
        this.currentRoom = target;
        this.shouldSwitch = true;
        const roomNameDict = ['office', 'hallway', 'kitchen'];
        this.sendMessage.emit(
          `Jeff ${this.randomTravel()} to the ${roomNameDict[target]}.`
        );
      }
    };
  }

  keyboard(value: string) {
    let key: any = {};
    key.value = value;
    key.isDown = false;
    key.isUp = true;
    // The `downHandler`
    key.downHandler = event => {
      if (event.key === key.value) {
        if (key.isUp && key.press) {
          key.press();
        }
        key.isDown = true;
        key.isUp = false;
        event.preventDefault();
      }
    };

    // The `upHandler`
    key.upHandler = event => {
      if (event.key === key.value) {
        if (key.isDown && key.release) {
          key.release();
        }
        key.isDown = false;
        key.isUp = true;
        event.preventDefault();
      }
    };

    // Attach event listeners
    const downListener = key.downHandler.bind(key);
    const upListener = key.upHandler.bind(key);

    this.el.nativeElement.addEventListener('keydown', downListener, false);
    this.el.nativeElement.addEventListener('keyup', upListener, false);

    // Detach event listeners
    key.unsubscribe = () => {
      this.el.nativeElement.removeEventListener('keydown', downListener);
      this.el.nativeElement.removeEventListener('keyup', upListener);
    };

    return key;
  }

  isColliding(o1, o2) {
    const dx = Math.abs(o1.x - o2.x);
    const dy = Math.abs(o1.y - o2.y);
    const lx = (o1.width + o2.width) / 2;
    const ly = (o1.height + o2.height) / 2;
    return dx < lx && dy < ly;
  }

  contains(r, o) {
    return (
      o.x >= r.x && o.x <= r.x + r.width && o.y >= r.y && o.y <= r.y + r.height
    );
  }

  randomTravel() {
    const textArray = ['travelled', 'moved', 'journeyed'];
    const randomNumber = Math.floor(Math.random() * textArray.length);
    return textArray[randomNumber];
  }

  randomPickUp() {
    const textArray = ['grabbed', 'picked up', 'took'];
    const randomNumber = Math.floor(Math.random() * textArray.length);
    return textArray[randomNumber];
  }

  randomDrop() {
    const textArray = ['dropped', 'put down', 'discarded'];
    const randomNumber = Math.floor(Math.random() * textArray.length);
    return textArray[randomNumber];
  }
}
