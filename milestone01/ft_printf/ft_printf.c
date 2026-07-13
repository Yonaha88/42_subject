/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/02 14:47:32 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/08 17:05:44 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "ft_printf.h"

static int	ft_put_unknown_spec(const char c, int len)
{
	if (c == '\0')
		return (-1);
	len = ft_putchar('%', len);
	len = ft_putchar(c, len);
	return (len);
}

static int	ft_printf_spec(const char *format, int idx, int len, va_list ap)
{
	const char	*hex_base = "0123456789abcdef";

	if (format[idx] == 'c')
		len = ft_putchar(va_arg(ap, int), len);
	else if (format[idx] == 's')
		len = ft_putstr(va_arg(ap, char *), len);
	else if (format[idx] == 'p')
		len = ft_putptr(va_arg(ap, void *), len, hex_base);
	else if (format[idx] == 'u')
		len = ft_putnbr((long)va_arg(ap, unsigned int), len);
	else if (format[idx] == 'i' || format[idx] == 'd')
		len = ft_putnbr((long)va_arg(ap, int), len);
	else if (format[idx] == 'x')
		len = ft_puthex((unsigned long long)va_arg(ap, unsigned int),
				len, hex_base);
	else if (format[idx] == 'X')
		len = ft_puthex((unsigned long long)va_arg(ap, unsigned int),
				len, "0123456789ABCDEF");
	else if (format[idx] == '%')
		len = ft_putchar('%', len);
	else
		len = ft_put_unknown_spec(format[idx], len);
	return (len);
}

int	ft_printf(const char *format, ...)
{
	va_list	ap;
	int		idx;
	int		len;

	va_start(ap, format);
	idx = 0;
	len = 0;
	while (format[idx])
	{
		if (format[idx] == '%')
		{
			idx++;
			len = ft_printf_spec(format, idx, len, ap);
		}
		else
			len = ft_putchar(format[idx], len);
		if (len < 0)
			break ;
		idx++;
	}
	va_end(ap);
	return (len);
}
