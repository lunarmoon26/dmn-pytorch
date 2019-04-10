import { NgModule } from '@angular/core';
import {
  MatButtonModule,
  MatToolbarModule,
  MatIconModule,
  MatInputModule
} from '@angular/material';

@NgModule({
  imports: [MatButtonModule, MatToolbarModule, MatIconModule, MatInputModule],
  exports: [MatButtonModule, MatToolbarModule, MatIconModule, MatInputModule]
})
export class AppMaterialModule {}
