import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AboutComponent } from './about/about.component';
import { BoardComponent } from './board/board.component';

const routes: Routes = [
  { path: '', redirectTo: '/board', pathMatch: 'full' },
  // { path: 'about', component: AboutComponent },
  { path: 'board', component: BoardComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
