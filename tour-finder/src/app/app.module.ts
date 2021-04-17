import { BrowserModule } from '@angular/platform-browser';
import {LOCALE_ID, NgModule} from '@angular/core';

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
import {TestGoogleComponent} from './test-google/test-google.component';
import {registerLocaleData} from '@angular/common';
import localeDe from '@angular/common/locales/de';
import { AlertComponent } from './alert/alert.component';
import { LayoutComponent } from './layout/layout.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { UserLayoutComponent } from './user-layout/user-layout.component';
import { UserListComponent } from './user-list/user-list.component';
import {AuthInterceptor} from './shared/auth.interceptor';

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
    TestGoogleComponent,
    AlertComponent,
    LayoutComponent,
    LoginComponent,
    RegisterComponent,
    UserLayoutComponent,
    UserListComponent
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
      useClass: AuthInterceptor,
      multi: true,

    },
    { provide: LOCALE_ID, useValue: 'de'}
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
  constructor() {
    registerLocaleData(localeDe);
  }
}
