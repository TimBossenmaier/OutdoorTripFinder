import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { TourDetailsComponent } from './tour-details/tour-details.component';
import { TourListComponent } from './tour-list/tour-list.component';
import { TourListItemComponent } from './tour-list-item/tour-list-item.component';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';
import {SearchComponent} from './search/search.component';
import {CommentComponent} from './comment/comment.component';
import {TourSearchComponent} from './tour-search/tour-search.component';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {TokenInterceptor} from './shared/token.interceptor';
import {TestGoogleComponent} from './test-google/test-google.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    TourDetailsComponent,
    TourListComponent,
    TourListItemComponent,
    SearchComponent,
    CommentComponent,
    TourSearchComponent,
    TestGoogleComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    BrowserAnimationsModule
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: TokenInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
