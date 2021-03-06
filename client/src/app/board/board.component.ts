import { Component, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-board',
  templateUrl: './board.component.html',
  styleUrls: ['./board.component.scss']
})
export class BoardComponent implements OnInit {
  eventLogs = [];
  question = '';
  get eventLogsText() {
    return this.eventLogs.join('\n');
  }

  constructor(private apiService: ApiService) {}

  ngOnInit() {}

  onSubmit(f: NgForm) {
    this.apiService.postLines(this.eventLogs).subscribe(response => {
      console.log(response);
    });
  }

  postQuestion(q: string) {
    if (q) {
      this.eventLogs.push(q);
      this.question = '';
    }
  }
  onMessageSent(msg: string) {
    if (msg) {
      this.eventLogs.push(msg);
    }
  }
}
