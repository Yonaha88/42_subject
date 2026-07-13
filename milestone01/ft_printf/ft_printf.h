/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/02 14:45:06 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/07 17:34:14 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef FT_PRINTF_H
# define FT_PRINTF_H

# include <unistd.h>
# include <stdarg.h>
# include <stdlib.h>

int		ft_printf(const char *format, ...);
int		ft_putchar(char c, int len);
int		ft_putstr(const char *str, int len);
int		ft_puthex(unsigned long long n, int len, const char *hex_base);
char	*ft_itoa(long nbr);
int		ft_putnbr(long n, int len);
int		ft_putptr(void *n, int len, const char *hex_base);

#endif