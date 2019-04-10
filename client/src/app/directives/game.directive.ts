import {
  Directive,
  ElementRef,
  OnInit,
  Output,
  EventEmitter,
  OnDestroy
} from '@angular/core';
import * as PIXI from 'pixi.js';

const GAME_HEIGHT = 600;
const GAME_WIDTH = 800;
const MOVE_SPEED = 2;

@Directive({
  selector: '[appGame]'
})
export class GameDirective implements OnInit, OnDestroy {
  @Output() sendMessage = new EventEmitter<string>();

  private dungeon;
  private explorer;
  private explorerGroup;
  private treasure;
  private door;
  private app: PIXI.Application;
  private controls = [];

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
    this.controls.forEach(c => {
      c.unsubscribe();
    });
  }

  setup() {
    this.dungeon = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures[
        'dungeon.png'
      ]
    );
    this.app.stage.addChild(this.dungeon);

    this.door = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures['door.png']
    );
    this.door.position.set(32, 0);
    this.app.stage.addChild(this.door);

    this.treasure = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures[
        'treasure.png'
      ]
    );
    this.treasure.x = this.app.stage.width - this.treasure.width - 48;
    this.treasure.y = this.app.stage.height / 2 - this.treasure.height / 2;
    this.app.stage.addChild(this.treasure);

    this.explorerGroup = new PIXI.Container();
    this.explorer = new PIXI.Sprite(
      PIXI.loader.resources['assets/treasureHunter.json'].textures[
        'explorer.png'
      ]
    );
    this.explorerGroup.x = 68;
    this.explorerGroup.y = this.app.stage.height / 2 - this.explorer.height / 2;
    this.explorerGroup.vx = 0;
    this.explorerGroup.vy = 0;
    this.explorerGroup.addChild(this.explorer);
    this.app.stage.addChild(this.explorerGroup);

    this.setupControls();
    const rightBound = 460;
    const leftBound = 32;
    const upperBound = 16;
    const lowerBound = 448;
    this.app.ticker.add(delta => {
      if (
        this.explorerGroup.x <= rightBound &&
        this.explorerGroup.x >= leftBound
      ) {
        this.explorerGroup.x += this.explorerGroup.vx;
      } else if (this.explorerGroup.x > rightBound) {
        this.explorerGroup.x = rightBound;
      } else if (this.explorerGroup.x < leftBound) {
        this.explorerGroup.x = leftBound;
      }

      if (
        this.explorerGroup.y <= lowerBound &&
        this.explorerGroup.y >= upperBound
      ) {
        this.explorerGroup.y += this.explorerGroup.vy;
      } else if (this.explorerGroup.y > lowerBound) {
        this.explorerGroup.y = lowerBound;
      } else if (this.explorerGroup.y < upperBound) {
        this.explorerGroup.y = upperBound;
      }
    });
  }

  setupControls() {
    // Capture the keyboard arrow keys
    const left = this.keyboard('ArrowLeft');
    const up = this.keyboard('ArrowUp');
    const right = this.keyboard('ArrowRight');
    const down = this.keyboard('ArrowDown');
    this.controls.push(left);
    this.controls.push(up);
    this.controls.push(right);
    this.controls.push(down);

    // Left arrow key `press` method
    left.press = () => {
      // Change the explorerGroup's velocity when the key is pressed
      this.explorerGroup.vx = -MOVE_SPEED;
      this.explorerGroup.vy = 0;
      this.sendMessage.emit("Tony moved to left.");
    };

    // Left arrow key `release` method
    left.release = () => {
      // If the left arrow has been released, and the right arrow isn't down,
      // and the explorerGroup isn't moving vertically:
      // Stop the explorerGroup
      if (!right.isDown && this.explorerGroup.vy === 0) {
        this.explorerGroup.vx = 0;
      }
    };

    // Up
    up.press = () => {
      this.explorerGroup.vy = -MOVE_SPEED;
      this.explorerGroup.vx = 0;
      this.sendMessage.emit("Tony moved to up.");
    };
    up.release = () => {
      if (!down.isDown && this.explorerGroup.vx === 0) {
        this.explorerGroup.vy = 0;
      }
    };

    // Right
    right.press = () => {
      this.explorerGroup.vx = MOVE_SPEED;
      this.explorerGroup.vy = 0;
      this.sendMessage.emit("Tony moved to right.");
    };
    right.release = () => {
      if (!left.isDown && this.explorerGroup.vy === 0) {
        this.explorerGroup.vx = 0;
      }
    };

    // Down
    down.press = () => {
      this.explorerGroup.vy = MOVE_SPEED;
      this.explorerGroup.vx = 0;
      this.sendMessage.emit("Tony moved to down.");
    };
    down.release = () => {
      if (!up.isDown && this.explorerGroup.vx === 0) {
        this.explorerGroup.vy = 0;
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

    window.addEventListener('keydown', downListener, false);
    window.addEventListener('keyup', upListener, false);

    // Detach event listeners
    key.unsubscribe = () => {
      window.removeEventListener('keydown', downListener);
      window.removeEventListener('keyup', upListener);
    };

    return key;
  }
}
